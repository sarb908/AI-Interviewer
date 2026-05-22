import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
from dotenv import load_dotenv

# Find the project root directory (parent of the directory containing auth.py)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")

# Load environment variables from the project root's .env file
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# Get credentials configuration
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        if firebase_json:
            print("Firebase Auth: Initializing using FIREBASE_SERVICE_ACCOUNT_JSON env var...")
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase Auth: Initialized successfully using JSON env var.")
        else:
            # Resolve cred_path relative to project root if it's a relative path
            resolved_cred_path = cred_path
            if cred_path and not os.path.isabs(cred_path):
                resolved_cred_path = os.path.abspath(os.path.join(project_root, cred_path))

            if resolved_cred_path and os.path.exists(resolved_cred_path):
                print(f"Firebase Auth: Initializing using local file path: {resolved_cred_path}...")
                cred = credentials.Certificate(resolved_cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Auth: Initialized successfully using local file.")
            else:
                # Log a clear warning about missing configuration
                path_msg = f"Path resolved to: {resolved_cred_path}" if resolved_cred_path else "No path provided"
                print(f"Firebase Auth WARNING: Service account key not found ({path_msg}). Falling back to default credentials.")
                firebase_admin.initialize_app()
                print("Firebase Auth: Initialized using default credentials.")
except Exception as e:
    # Log the warning but don't crash startup immediately; route calls will fail if not configured
    print(f"Firebase Auth WARNING: Firebase Admin SDK failed to initialize: {e}")

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to verify the Firebase ID token in the Authorization header.
    Returns the decoded token dictionary if valid, otherwise raises 401.
    """
    token = credentials.credentials
    try:
        # verify_id_token checks expiration, signature, and audience
        print("Firebase Auth: Attempting to verify token...")
        decoded_token = auth.verify_id_token(token)
        print(f"Firebase Auth: Token verified successfully. User UID: {decoded_token.get('uid')}")
        return decoded_token
    except Exception as e:
        print(f"Firebase Auth ERROR: Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
