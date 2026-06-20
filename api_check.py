from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from security import decode_token
from jose import JWTError

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials  # pulls the raw token out of "Bearer <token>"

    try:
        payload = decode_token(token)  # verifies signature + expiry
        user_id = payload.get("sub")  # "sub" is where we stored the user id
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}  # this gets passed into your route
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")