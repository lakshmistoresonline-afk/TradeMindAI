import os
import firebase_admin
from firebase_admin import auth, credentials
import json

# Path to service account
SERVICE_ACCOUNT_PATH = 'backend/service-account.json'

def create_user(email, password):
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"Error: {SERVICE_ACCOUNT_PATH} not found.")
        return

    try:
        # Initialize Firebase Admin if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)

        print(f"[*] Creating/Updating user: {email}")

        try:
            # Check if user exists
            user = auth.get_user_by_email(email)
            print(f"   User already exists with UID: {user.uid}. Updating password...")
            auth.update_user(user.uid, password=password)
            print(f"[+] Password updated successfully.")
        except auth.UserNotFoundError:
            # Create new user
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=True
            )
            print(f"[+] User created successfully with UID: {user.uid}")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    import sys
    email = "admin@trademindai.com"
    password = "Admin@123"
    create_user(email, password)
