/**
 * Push notification service for mobile app.
 * 
 * Handles FCM token registration and notification handling.
 */

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from './api';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

const PUSH_TOKEN_STORAGE_KEY = 'push_token_registered';

export interface PushNotificationService {
  registerForPushNotifications: () => Promise<string | null>;
  unregisterPushToken: () => Promise<void>;
  getExpoPushToken: () => Promise<string | null>;
}

class PushNotificationServiceImpl implements PushNotificationService {
  private expoPushToken: string | null = null;

  /**
   * Register device for push notifications.
   * Returns Expo push token or null if registration failed.
   */
  async registerForPushNotifications(): Promise<string | null> {
    try {
      // Check if already registered
      const registered = await AsyncStorage.getItem(PUSH_TOKEN_STORAGE_KEY);
      if (registered === 'true' && this.expoPushToken) {
        return this.expoPushToken;
      }

      // Check if device supports push notifications
      if (!Device.isDevice) {
        console.warn('Push notifications only work on physical devices');
        return null;
      }

      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.warn('Failed to get push token for push notification!');
        return null;
      }

      // Get Expo push token
      const tokenData = await Notifications.getExpoPushTokenAsync({
        projectId: 'neurotrainer-6449b', // Firebase project ID
      });

      this.expoPushToken = tokenData.data;
      console.log('Expo push token:', this.expoPushToken);

      // Register token with backend
      await this.registerTokenWithBackend(this.expoPushToken);

      // Mark as registered
      await AsyncStorage.setItem(PUSH_TOKEN_STORAGE_KEY, 'true');

      return this.expoPushToken;
    } catch (error) {
      console.error('Error registering for push notifications:', error);
      return null;
    }
  }

  /**
   * Register push token with backend API.
   */
  private async registerTokenWithBackend(token: string): Promise<void> {
    try {
      await authAPI.registerPushToken({
        token,
        platform: Platform.OS === 'ios' ? 'ios' : 'android',
        device_id: await Device.modelName || undefined,
      });
      console.log('Token registered with backend:', token);
    } catch (error) {
      console.error('Error registering token with backend:', error);
    }
  }

  /**
   * Unregister push token.
   */
  async unregisterPushToken(): Promise<void> {
    try {
      if (this.expoPushToken) {
        await authAPI.unregisterPushToken(this.expoPushToken);
      }
      
      await AsyncStorage.removeItem(PUSH_TOKEN_STORAGE_KEY);
      this.expoPushToken = null;
      
      console.log('Push token unregistered');
    } catch (error) {
      console.error('Error unregistering push token:', error);
    }
  }

  /**
   * Get current Expo push token.
   */
  async getExpoPushToken(): Promise<string | null> {
    if (this.expoPushToken) {
      return this.expoPushToken;
    }

    return await this.registerForPushNotifications();
  }

  /**
   * Setup notification listeners.
   */
  setupNotificationListeners() {
    // Listener for notifications received while app is foregrounded
    Notifications.addNotificationReceivedListener((notification) => {
      console.log('Notification received:', notification);
    });

    // Listener for when user taps on notification
    Notifications.addNotificationResponseReceivedListener((response) => {
      console.log('Notification response:', response);
      // Handle notification tap (e.g., navigate to specific screen)
    });
  }
}

// Export singleton instance
export const pushNotificationService = new PushNotificationServiceImpl();

// Setup listeners on import
pushNotificationService.setupNotificationListeners();

