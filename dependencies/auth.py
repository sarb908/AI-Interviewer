import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
from dotenv import load_dotenv

load_dotenv()

# Get credentials configuration
firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        if firebase_json:
            # Initialize using credentials JSON string (recommended for Vercel)
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to default credentials
            firebase_admin.initialize_app()
except Exception as e:
    # Log the warning but don't crash startup immediately; route calls will fail if not configured
    print(f"Warning: Firebase Admin SDK failed to initialize: {e}")

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to verify the Firebase ID token in the Authorization header.
    Returns the decoded token dictionary if valid, otherwise raises 401.
    """
    token = credentials.credentials
    try:
        # verify_id_token checks expiration, signature, and audience
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
