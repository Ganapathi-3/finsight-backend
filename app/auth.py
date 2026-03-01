from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os

# ==============================
# CONFIG
# ==============================

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],  # ✅ NO BCRYPT
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==============================
# FAKE USER DATABASE
# ==============================

# 🔥 Replace this hash with your generated pbkdf2 hash
SAMPLE_HASH = "$pbkdf2-sha256$29000$xziHECIkJIRQKiXEuLcWAg$eBS2OleCmuMl7VWoQ6TTv7k6JrWGCGiwxJLKsl6DIxc"

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "$pbkdf2-sha256$29000$.x8jJISwFkJIKcXYm7M25g$NwmqGIZvp7Cvk9uIS2s03LImam3iqA7UCjFaVSiDSOE",
        "role": "admin"
    },
    "finance": {
        "username": "finance",
        "hashed_password": "$pbkdf2-sha256$29000$NUboHcP4f6.V8r5XSumdEw$eEepRuRiNjEX4QxRacFl/RPKRAnEjsrD3e0MNdaQJaI",
        "role": "finance"
    },
    "hr": {
        "username": "hr",
        "hashed_password": "$pbkdf2-sha256$29000$JIRQCgGAUKq11ro3xpgTQg$OKXO/cHz1oC0V0JSrSySIQEC4PogsNwd1B.p30tLfTc",
        "role": "hr"
    },
    "executive": {
        "username": "executive",
        "hashed_password": "$pbkdf2-sha256$29000$IgRAKGUMYYyxVkppzVnLeQ$0itQISXmU7.yGR5/jNn3HseUNxFRoMrE8S989UQcqeI",
        "role": "executive"
    }
}
# ==============================
# PASSWORD FUNCTIONS
# ==============================

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

# ==============================
# JWT FUNCTIONS
# ==============================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return {"username": username, "role": role}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ==============================
# ROLE-BASED ACCESS CONTROL
# ==============================

def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient role privileges"
            )
        return current_user
    return role_checker
