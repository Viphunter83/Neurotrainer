# Environment Variables Setup Guide

## Quick Setup

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Fill in the required values (see below)

3. For React Native, you may need to use `react-native-config` or similar

## Required Variables

### 1. Sentry DSN

**Purpose**: Error tracking and monitoring

**How to get**:
1. Go to [Sentry.io](https://sentry.io)
2. Create a new project (React Native)
3. Copy the DSN from project settings
4. Add to `.env`: `SENTRY_DSN=your_dsn_here`

**Example**:
```
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/123456
```

### 2. AWS Credentials

**Purpose**: Deployment to AWS (ECS, ECR, RDS)

**How to get**:
1. Go to AWS Console → IAM
2. Create a new user with programmatic access
3. Attach policies:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonECS_FullAccess`
   - `AmazonRDSFullAccess`
   - `CloudWatchFullAccess`
4. Copy Access Key ID and Secret Access Key
5. Add to `.env`:
   ```
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   AWS_REGION=us-east-1
   AWS_ACCOUNT_ID=123456789012
   ```

**Security Note**: Never commit `.env` file to git!

### 3. Slack Webhook

**Purpose**: Deployment notifications

**How to get**:
1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app or use existing
3. Go to "Incoming Webhooks"
4. Activate Incoming Webhooks
5. Click "Add New Webhook to Workspace"
6. Select channel for notifications
7. Copy webhook URL
8. Add to `.env`:
   ```
   SLACK_WEBHOOK_URL=your_slack_webhook_url_here
   ```

## GitHub Secrets Setup

For CI/CD, add secrets to GitHub repository:

1. Go to repository → Settings → Secrets and variables → Actions
2. Add the following secrets:

### Required Secrets

- `SENTRY_DSN` - Sentry DSN for error tracking
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_ACCOUNT_ID` - AWS account ID
- `SLACK_WEBHOOK` - Slack webhook URL

### Optional Secrets

- `GOOGLE_ANALYTICS_ID` - Google Analytics ID
- `MIXPANEL_TOKEN` - Mixpanel token
- `DATABASE_URL` - Database connection string (for tests)

## Environment-Specific Configuration

### Development

```bash
NODE_ENV=development
API_URL=http://localhost:8000
LOG_LEVEL=DEBUG
```

### Staging

```bash
NODE_ENV=staging
API_URL=https://staging-api.fitnessai.com
LOG_LEVEL=INFO
```

### Production

```bash
NODE_ENV=production
API_URL=https://api.fitnessai.com
LOG_LEVEL=WARN
```

## React Native Configuration

For React Native, you may need to use `react-native-config`:

1. Install:
   ```bash
   npm install react-native-config
   ```

2. Create `.env` file in project root

3. Access in code:
   ```typescript
   import Config from 'react-native-config';
   
   const apiUrl = Config.API_URL;
   ```

4. Update native configs (iOS/Android) if needed

## Verification

After setup, verify configuration:

```bash
# Check environment variables are loaded
npm run test:unit

# Check Sentry is configured
# Look for Sentry initialization in logs

# Test Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'
```

## Security Best Practices

1. **Never commit `.env` files**
   - Add to `.gitignore`
   - Use `.env.example` as template

2. **Use different credentials for each environment**
   - Development, Staging, Production should have separate credentials

3. **Rotate credentials regularly**
   - Update AWS keys every 90 days
   - Rotate Slack webhooks if compromised

4. **Use least privilege**
   - Only grant necessary AWS permissions
   - Use separate IAM users for CI/CD

5. **Monitor access**
   - Enable AWS CloudTrail
   - Monitor Sentry for suspicious activity

## Troubleshooting

### Variables not loading

1. Check file is named `.env` (not `.env.local`)
2. Verify `react-native-config` is installed
3. Rebuild app: `npm run ios` or `npm run android`

### AWS credentials not working

1. Verify IAM user has correct permissions
2. Check AWS region matches
3. Verify credentials are not expired

### Slack webhook not working

1. Test webhook URL with curl
2. Check Slack app permissions
3. Verify channel exists and bot has access

