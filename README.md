# Asset Tracker App

A Streamlit-based web application for tracking assets, with Google Sheets as the database backend.

## Features

- ✅ User Registration and Login
- ✅ Mobile-responsive design (works on Android, iPhone, and tablets)
- ✅ Google Sheets integration for data storage
- ✅ Secure password hashing

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Sheets Authentication

You have two options to configure Google Sheets authentication:

#### Option A: Using Streamlit Secrets (Recommended for deployment)

1. Create a `.streamlit/secrets.toml` file in your project root
2. Add your Google Cloud service account credentials:

```toml
google_credentials = {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

#### Option B: Using Credentials File

1. Download your service account JSON key from Google Cloud Console
2. Save it as `credentials.json` in the project root directory
3. Make sure the service account has access to your Google Sheet

### 3. Google Sheet Setup

The app expects a Google Sheet with the following:
- Sheet ID: `1q9jfezVWpFYAmvjo81Lk788kf9DNwqvSx7yxHWRGkec`
- A sheet named "Users" (will be created automatically if it doesn't exist)

The "Users" sheet will have the following columns:
- username
- email
- password_hash
- created_at
- last_login

### 4. Run the Application

```bash
streamlit run app_streamlit.py
```

The app will open in your default web browser at `http://localhost:8501`

## Mobile Responsiveness

The app is designed to be fully responsive and will automatically adjust to:
- Mobile phones (Android/iOS)
- Tablets
- Desktop browsers

## Usage

1. **Register**: Click "Go to Register" to create a new account
2. **Login**: Use your username/email and password to log in
3. After successful login, you'll see the dashboard (currently a placeholder)

## Security Notes

- Passwords are hashed using SHA256 before storage
- Never commit `credentials.json` or `.streamlit/secrets.toml` to version control
- Add these files to your `.gitignore`

## Next Steps

The current implementation includes only login and registration functionality. Additional features can be added to the dashboard after authentication.

