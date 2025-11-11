"""
Push notification service using Firebase Cloud Messaging (FCM).

Handles sending push notifications to mobile devices.
"""

import json
import logging
from typing import List, Optional
from uuid import UUID

import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session

from src.config import settings
from src.database.database import get_db
from src.database.models import PushToken, User

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_app: Optional[firebase_admin.App] = None


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK."""
    global _firebase_app
    
    if _firebase_app is not None:
        return
    
    if not settings.FIREBASE_CREDENTIALS_PATH:
        logger.warning("FIREBASE_CREDENTIALS_PATH not set. Push notifications will be disabled.")
        return
    
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        raise


def get_firebase_app() -> Optional[firebase_admin.App]:
    """Get Firebase app instance."""
    if _firebase_app is None:
        initialize_firebase()
    return _firebase_app


async def send_push_notification(
    user_id: UUID,
    title: str,
    body: str,
    data: Optional[dict] = None,
    db: Optional[Session] = None,
) -> bool:
    """
    Send push notification to a user's devices.
    
    Args:
        user_id: User ID to send notification to
        title: Notification title
        body: Notification body
        data: Optional data payload
        db: Database session (if None, creates new)
        
    Returns:
        True if notification was sent successfully, False otherwise
    """
    if not get_firebase_app():
        logger.warning("Firebase not initialized. Cannot send push notification.")
        return False
    
    # Get database session
    if db is None:
        db_gen = get_db()
        db = next(db_gen)
        try:
            return await _send_notification_internal(user_id, title, body, data, db)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass
    else:
        return await _send_notification_internal(user_id, title, body, data, db)


async def _send_notification_internal(
    user_id: UUID,
    title: str,
    body: str,
    data: Optional[dict],
    db: Session,
) -> bool:
    """Internal function to send notification."""
    # Get active push tokens for user
    tokens = db.query(PushToken).filter(
        PushToken.user_id == user_id,
        PushToken.is_active == True,  # noqa: E712
    ).all()
    
    if not tokens:
        logger.info(f"No active push tokens found for user {user_id}")
        return False
    
    # Prepare notification
    notification = messaging.Notification(
        title=title,
        body=body,
    )
    
    # Prepare message data
    message_data = data or {}
    message_data["user_id"] = str(user_id)
    
    # Create messages for each token
    messages = []
    for token_obj in tokens:
        message = messaging.Message(
            notification=notification,
            data=message_data,
            token=token_obj.token,
            android=messaging.AndroidConfig(
                priority="high",
            ),
            apns=messaging.APNSConfig(
                headers={
                    "apns-priority": "10",
                },
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        badge=1,
                    ),
                ),
            ),
        )
        messages.append((message, token_obj))
    
    # Send notifications
    success_count = 0
    failed_tokens = []
    
    for message, token_obj in messages:
        try:
            response = messaging.send(message)
            logger.info(f"Successfully sent notification to token {token_obj.token[:20]}...")
            success_count += 1
            
            # Update last_used_at
            from datetime import datetime
            token_obj.last_used_at = datetime.utcnow()
            db.commit()
            
        except messaging.UnregisteredError:
            logger.warning(f"Token {token_obj.token[:20]}... is unregistered. Deactivating.")
            token_obj.is_active = False
            db.commit()
            failed_tokens.append(token_obj.token)
            
        except Exception as e:
            logger.error(f"Failed to send notification to token {token_obj.token[:20]}...: {e}")
            failed_tokens.append(token_obj.token)
    
    logger.info(
        f"Sent {success_count}/{len(messages)} notifications to user {user_id}. "
        f"Failed: {len(failed_tokens)}"
    )
    
    return success_count > 0


async def send_bulk_notification(
    user_ids: List[UUID],
    title: str,
    body: str,
    data: Optional[dict] = None,
    db: Optional[Session] = None,
) -> dict:
    """
    Send push notification to multiple users.
    
    Args:
        user_ids: List of user IDs
        title: Notification title
        body: Notification body
        data: Optional data payload
        db: Database session
        
    Returns:
        Dictionary with success and failure counts
    """
    results = {"success": 0, "failed": 0, "total": len(user_ids)}
    
    for user_id in user_ids:
        try:
            success = await send_push_notification(user_id, title, body, data, db)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {e}")
            results["failed"] += 1
    
    return results

