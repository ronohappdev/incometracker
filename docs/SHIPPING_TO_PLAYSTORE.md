# Shipping Income Tracker to Google Play Store - Complete Guide

This guide covers everything needed to deploy the Income Tracker app from development to production on Google Play Store.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Prepare Backend](#phase-1-prepare-backend)
3. [Phase 2: Prepare Mobile App](#phase-2-prepare-mobile-app)
4. [Phase 3: Build APK/AAB](#phase-3-build-apkaab)
5. [Phase 4: Google Play Console Setup](#phase-4-google-play-console-setup)
6. [Phase 5: Submit to Play Store](#phase-5-submit-to-play-store)
7. [Phase 6: Post-Launch](#phase-6-post-launch)

---

## Prerequisites

### Required Tools & Accounts

- ✅ Google Play Developer Account ($25 one-time fee)
- ✅ Android SDK & Android Studio (already needed for builds)
- ✅ Java Development Kit (JDK 11+)
- ✅ Keystore file for signing APKs (create once, keep secure)
- ✅ Production server hosting (AWS, Heroku, DigitalOcean, etc.)
- ✅ PostgreSQL database in production
- ✅ SSL certificate for API (required for HTTPS)

### Current App Status

- ✅ Backend: All endpoints implemented and tested
- ✅ Mobile: All core features complete
- ✅ Tests: 9 passing unit tests for calculations
- ✅ TypeScript: Strict mode, no errors
- ✅ Platform Support: Works on web, iOS (via Expo), Android (native build required)

---

## Phase 1: Prepare Backend

### Step 1.1: Set Up Production Database

**Goal**: Create a production-grade PostgreSQL database

```bash
# Option A: AWS RDS (Recommended for production)
# - Create RDS PostgreSQL instance (t3.micro for free tier)
# - Configure security groups to allow FastAPI server access
# - Enable automated backups (7-30 days)
# - Enable encryption at rest
# - Note: DATABASE_URL = postgresql://user:password@host:5432/incometracker

# Option B: DigitalOcean Managed Database
# - Simpler setup than AWS
# - Built-in backups
# - Good for small-medium apps

# Option C: Self-hosted (not recommended for production)
# - More control but requires maintenance
# - No automatic backups unless you set them up
```

**Important**: Use a strong random password. Store credentials in a secure vault (AWS Secrets Manager, 1Password, LastPass).

### Step 1.2: Set Up Production Server

**Option A: AWS Elastic Container Service (ECS) - Recommended**

```bash
# Create ECR repository for Docker image
aws ecr create-repository --repository-name incometracker-api

# Build and push Docker image
cd backend
docker build -t incometracker-api:latest .
docker tag incometracker-api:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/incometracker-api:latest
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/incometracker-api:latest

# Create ECS cluster and task definition (use AWS Console or AWS CLI)
# - Allocate: 512 MB RAM, 0.25 CPU (sufficient for income tracker)
# - Set environment variables: DATABASE_URL, JWT_SECRET, CORS_ORIGINS
```

**Option B: Heroku (Easiest, but more expensive)**

```bash
# Install Heroku CLI
npm install -g heroku

# Login and create app
heroku login
heroku create incometracker-api

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set JWT_SECRET=your_secure_random_key
heroku config:set CORS_ORIGINS=https://yourapp.com

# Deploy
git push heroku main  # or your branch
```

**Option C: DigitalOcean App Platform**

```bash
# Connect GitHub repo
# Select backend/ directory as app source
# Set DATABASE_URL environment variable
# Deploy (automatic CI/CD from GitHub)
```

### Step 1.3: Run Database Migrations

```bash
# After database is created and server is deployed:
# SSH into server or use ECS task override
cd backend
alembic upgrade head

# This applies all migrations:
# - 0001_initial.py: Users, Income, Benchmark tables
# - 0002_benchmark_history.py: Salary history and adjustments
```

### Step 1.4: Test Production API

```bash
# Replace with your actual production URL
PROD_URL="https://api.yourdomain.com"

# Test health
curl $PROD_URL/docs  # Should show Swagger UI

# Test auth
curl -X POST $PROD_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Should return: {"access_token": "...", "token_type": "bearer"}
```

**Common Issues**:

- ❌ CORS errors: Ensure `CORS_ORIGINS` includes your app URL
- ❌ Database connection: Check DATABASE_URL format
- ❌ JWT errors: Verify JWT_SECRET is set

---

## Phase 2: Prepare Mobile App

### Step 2.1: Update API URL

**File**: [mobile/app.json](mobile/app.json)

```json
{
  "expo": {
    "plugins": [["expo-secure-store", {}]],
    "extra": {
      "API_URL": "https://api.yourdomain.com"
    }
  }
}
```

**File**: [mobile/services/api.ts](mobile/services/api.ts)

```typescript
// Update at top of file
const API_URL = process.env.EXPO_PUBLIC_API_URL || "https://api.yourdomain.com";
```

### Step 2.2: Update App Metadata

**File**: [mobile/app.json](mobile/app.json)

```json
{
  "expo": {
    "name": "Income Tracker",
    "slug": "income-tracker",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#0F172A"
    },
    "assetBundlePatterns": ["**/*"],
    "ios": {
      "supportsTabletMode": true,
      "bundleIdentifier": "com.yourcompany.incometracker"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#0F172A"
      },
      "package": "com.yourcompany.incometracker"
    },
    "web": {
      "favicon": "./assets/favicon.png"
    }
  }
}
```

**Critical Fields**:

- `version`: Must increment for each release (1.0.0 → 1.0.1)
- `android.package`: Must be unique (reverse domain notation)
- `icon.png`: 1024x1024 PNG
- `adaptive-icon.png`: 1024x1024 for Android adaptive icon

### Step 2.3: Create App Icons & Splash Screens

**Required Assets**:

```
mobile/assets/
├── icon.png (1024x1024) - Required for all platforms
├── splash.png (1242x2436) - iOS splash screen
├── adaptive-icon.png (1024x1024) - Android adaptive icon
└── favicon.png (192x192) - Web favicon
```

**Tools**:

- Figma (free): Design custom icon
- Expo Icon Creator: Auto-generate from image
- Canva: Free design templates
- https://app.icons8.com/: Quick icon generation

### Step 2.4: Update App Name & Description

**File**: [mobile/app.json](mobile/app.json)

```json
{
  "expo": {
    "description": "Track your income and compare against career benchmarks. Understand your financial progress with personalized analytics.",
    "owner": "yourcompany"
  }
}
```

### Step 2.5: Remove Development Dependencies

```bash
cd mobile

# Remove dev-only packages (if any)
npm uninstall expo-dev-client  # Only needed if you used it

# Verify clean dependencies
npm audit fix
```

---

## Phase 3: Build APK/AAB

### Step 3.1: Create Signing Keystore

**Only do this once! Store the keystore and password securely.**

```bash
# Generate keystore (valid for 10,000 days ≈ 27 years)
keytool -genkey-dname "cn=Your Name, ou=Company, o=Company, c=US" \
  -alias incometracker \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -keystore incometracker.keystore \
  -storepass YOUR_STORE_PASSWORD \
  -keypass YOUR_KEY_PASSWORD

# Verify keystore
keytool -list -v -keystore incometracker.keystore -storepass YOUR_STORE_PASSWORD
```

**Security**:

- ⚠️ NEVER commit keystore to Git
- ⚠️ Store securely (password manager)
- ⚠️ If lost, you cannot update existing app (different signing key)
- ✅ Use different passwords for store and key

### Step 3.2: Build Android App Bundle (AAB)

**Recommended**: App Bundle is smaller and Play Store handles device-specific APKs

```bash
cd mobile

# Install EAS CLI (Expo's build service)
npm install -g eas-cli

# Login to Expo account
eas login

# Configure build
eas build:configure --platform android

# Build for production
eas build --platform android --auto-submit  # Uses your keystore from Expo servers
```

**Alternative: Local Build (without EAS)**

```bash
# Install Android SDK build tools
# Open backend/Dockerfile for reference

# Build APK locally
cd mobile
eas build --platform android --local

# This creates: /mobile/android/app/build/outputs/apk/release/app-release.apk
```

**Build Time**: 5-15 minutes (first build slower)

### Step 3.3: Verify Built APK

```bash
# List contents (verify it's a valid APK)
unzip -l app-release.apk | head -20

# Check signing certificate
keytool -printcert -jarfile app-release.apk
```

---

## Phase 4: Google Play Console Setup

### Step 4.1: Create Developer Account

1. Go to **[Google Play Console](https://play.google.com/console)**
2. Sign in with Google account
3. Pay $25 registration fee
4. Complete account details:
   - Developer name
   - Email address
   - Website/store URL
5. Agree to agreements and policies

### Step 4.2: Create App in Play Console

1. Click **Create app**
2. Fill in:
   - **App name**: "Income Tracker"
   - **Default language**: English
   - **App type**: Application (not game)
   - **Category**: Finance
   - **Free or paid**: Free (can monetize later)
3. Click **Create app**

### Step 4.3: Complete App Information

**Navigate to**: App information → App details

Fill in:

- **Short description** (80 characters): "Track income & benchmark career progress"
- **Full description** (4000 characters):

  ```
  Income Tracker helps you understand your financial progress by comparing
  your actual income against personalized career benchmarks.

  Features:
  • Record income transactions from multiple sources
  • Set career benchmarks based on employment start date
  • View real-time progress charts
  • Monthly and yearly analytics
  • Secure, private data storage

  Whether you're tracking side hustles, freelance income, or career progression,
  Income Tracker provides the clarity you need to make informed decisions about
  your financial future.
  ```

- **Contact email**: your@email.com
- **Website**: (optional, leave blank if none)
- **Privacy policy URL**: (required - create at privacy.com or termly.com)

### Step 4.4: Complete Content Rating

**Navigate to**: Content rating questionnaire

Answer questions about:

- Violence, sex, profanity, etc.
- For finance app: Select "No" for all offensive content
- Submit to get content rating certificate (instant)

### Step 4.5: Set Target Audience

**Navigate to**: Target audience

- **Age group**: Users 18+ (financial management)
- **Intended users**: Adults
- **Directed to children**: No

### Step 4.6: Set Pricing & Distribution

**Navigate to**: Pricing and distribution

- **Countries**: Select all (or your preference)
- **Content rating certificate**: Already generated
- **Free or paid**: Free (or Premium if monetizing)

---

## Phase 5: Submit to Play Store

### Step 5.1: Upload App Bundle

**Navigate to**: Release → Production

1. Click **Create new release**
2. Click **Upload** under "App bundles"
3. Select your **app-release.aab** file (from Phase 3.2)
4. Wait for upload to complete (~1 minute)

**Play Console will validate**:

- ✅ Signing certificate matches your account
- ✅ Version number is higher than previous
- ✅ APK size is reasonable
- ✅ No malware/suspicious code

### Step 5.2: Add Release Notes

In the release notes field:

```
Release 1.0.0 - Initial Launch

• Record income from multiple sources
• Compare against personalized career benchmarks
• Monthly and yearly analytics
• Secure data storage with device encryption
• Free to use, no ads or premium features

Thanks for using Income Tracker!
```

### Step 5.3: Review Before Release

Before clicking **Save and review for release**:

✅ Verify:

- App icon displayed correctly
- Description matches what users see
- Version number correct (1.0.0 for launch)
- Screenshots added (see Step 4.7)
- Privacy policy URL works
- Permissions list is accurate (for location, contacts, etc.)

### Step 5.4: Add Screenshots (Critical for Downloads)

**Navigate to**: Product pages → Screenshots

Required:

- **Phone screenshots**: 2-5 images (1080x1920 pixels)
- **Tablet screenshots** (optional): 1280x1920 pixels

**Screenshots to add**:

1. Login screen with tagline
2. Dashboard showing empty state
3. Adding first income transaction
4. Dashboard with data
5. Analytics view

**Tools**:

- Take real screenshots from phone emulator
- Edit in Figma/Canva to add text overlays
- Use screenshot templates: figma.com/community (search "app screenshot")

### Step 5.5: Submit for Review

Click **Save and review for release** → **Submit**

**Review Timeline**:

- Usually 2-24 hours
- Check email for approval or rejection
- Most rejections are fixable (update privacy policy, remove bugs, etc.)

**Common Rejection Reasons**:

- ❌ App crashes on launch → Fix bug, rebuild, resubmit
- ❌ Missing privacy policy → Add link in app.json
- ❌ Uses restricted API without permission → Remove or request access
- ❌ Doesn't match screenshots → Update screenshots or fix UI

---

## Phase 6: Post-Launch

### Step 6.1: Enable Monitoring

**Backend**:

```bash
# Set up error tracking (Sentry, DataDog, etc.)
# Add: pip install sentry-sdk
# Initialize in backend/app/main.py:

import sentry_sdk
sentry_sdk.init("https://your-sentry-key@sentry.io/project-id")
```

**Mobile**:

```bash
# Add Expo error tracking
# Already built-in: expo-dev-menu for crash reporting
```

### Step 6.2: Set Up Analytics

```bash
# Google Analytics for Firebase
npm install firebase
# Configure in mobile/app/_layout.tsx
```

### Step 6.3: Monitor Server Health

**Set up uptime monitoring**:

- UptimeRobot (free): Ping API every 5 minutes
- PagerDuty: Alert on errors
- CloudWatch (AWS): Monitor ECS tasks

```bash
# Simple health check
curl -X GET https://api.yourdomain.com/docs
# Should return 200 status if server is up
```

### Step 6.4: Plan Version Updates

Create a release schedule:

- **v1.0.1**: Bug fixes (1-2 weeks after launch)
- **v1.1.0**: Feature additions (quarterly)
- **v2.0.0**: Major redesign (yearly)

Each update:

1. Increment version in app.json
2. Build new AAB
3. Add release notes
4. Submit to Play Store

---

## Troubleshooting

### Issue: "App crashes on startup"

**Fix**:

```bash
# Check logs
adb logcat | grep "incometracker"

# Common causes:
# - API_URL not set correctly
# - Database migrations not applied
# - JWT_SECRET not configured
```

### Issue: "Play Store rejects for security reasons"

**Fix**:

- Ensure API uses HTTPS (not HTTP)
- Remove any hardcoded passwords/keys
- Use environment variables for all secrets
- Run `npm audit fix` to update vulnerable packages

### Issue: "App takes too long to load"

**Fix**:

- Reduce initial data fetching (lazy load)
- Compress images in assets/
- Use React Query caching
- Monitor API response times

### Issue: "Users report wrong calculations"

**Fix**:

- Check backend calculations in services.py
- Verify database migrations applied correctly
- Test with known benchmark scenarios
- Push hotfix: bump version, rebuild, resubmit

---

## Checklist: Pre-Launch

- [ ] Backend deployed to production server
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] API tested and responding
- [ ] SSL certificate configured (HTTPS)
- [ ] Mobile app API_URL points to production
- [ ] App icons created (1024x1024 PNG)
- [ ] App name, description, screenshots ready
- [ ] Privacy policy written and URL added
- [ ] Keystore created and backed up
- [ ] APK/AAB built and tested locally
- [ ] Google Play Developer account created ($25)
- [ ] App created in Play Console
- [ ] All metadata filled in
- [ ] Screenshots uploaded (5 minimum)
- [ ] Content rating completed
- [ ] AAB uploaded for review
- [ ] Release notes written
- [ ] Monitoring set up (error tracking, analytics)

---

## After Launch: Marketing

- Share on social media: Twitter, LinkedIn, Indie Hackers
- Submit to ProductHunt: producthunt.com
- Post on relevant subreddits: r/finance, r/personalfinance
- Email beta testers: Ask for 5-star reviews
- Collect feedback: Create feedback form in Settings

---

## Timeline Estimate

| Phase                | Duration       | Notes                    |
| -------------------- | -------------- | ------------------------ |
| Backend setup        | 2-4 hours      | Database + server config |
| App preparation      | 1-2 hours      | Metadata + icons         |
| Build APK/AAB        | 15 minutes     | Via Expo EAS             |
| Play Console setup   | 1 hour         | Account + app info       |
| Screenshots + review | 2-3 hours      | Design + iteration       |
| Submission + review  | 2-24 hours     | Google's review time     |
| **Total**            | **8-36 hours** | Usually 1-2 days         |

---

## Support & Resources

- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [Expo Documentation](https://docs.expo.dev)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Android Developer Guide](https://developer.android.com)
- [React Native Platform-Specific Code](https://reactnative.dev/docs/platform-specific-code)

---

**Questions?** Review the [BUILD SPECIFICATION](../BUILD%20SPECIFICATION%20—%20PERSONAL%20INCOME%20GAP%20TRACKER.md) for feature requirements and [development-progress.md](development-progress.md) for current status.
