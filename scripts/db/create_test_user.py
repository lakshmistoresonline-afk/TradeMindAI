import os
import firebase_admin
from firebase_admin import auth, credentials

# Path to service account
SERVICE_ACCOUNT_PATH = 'backend/service-account.json'

def create_test_user(email, password):
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"Error: {SERVICE_ACCOUNT_PATH} not found.")
        return

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)

        print(f"[*] Creating/Updating test user: {email}")

        try:
            user = auth.get_user_by_email(email)
            print(f"   User already exists. Updating password...")
            auth.update_user(user.uid, password=password)
            print(f"[+] Password updated.")
        except auth.UserNotFoundError:
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=True,
                display_name="Test Terminal User"
            )
            print(f"[+] User created successfully. UID: {user.uid}")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    # Standard User (Non-Admin)
    create_test_user("user@trademind.ai", "User@123")
