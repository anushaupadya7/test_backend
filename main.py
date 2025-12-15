from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(title="File Upload API with Authentication")

# Create data folder if it doesn't exist
DATA_FOLDER = Path("data")
DATA_FOLDER.mkdir(exist_ok=True)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URL)
db = client[os.getenv("DB_NAME", "test_backend")]
files_collection = db["files"]  # Correct collection for file operations
users_collection = db["users"]  # Correct collection for creating users

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Pydantic models
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# Password hashing functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    # BUG: Reading from wrong collection! Should read from "users" but reads from "user_accounts"
    user_accounts_collection = db["user_accounts"]  
    user_data = user_accounts_collection.find_one({"username": username})
    if user_data:
        return UserInDB(**user_data)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Initialize dummy users on startup
def create_dummy_users():
    """Create 5 dummy users if they don't exist"""
    dummy_users = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "hashed_password": get_password_hash("password123"),
            "disabled": False
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "full_name": "Jane Smith",
            "hashed_password": get_password_hash("password123"),
            "disabled": False
        },
        {
            "username": "bob_wilson",
            "email": "bob@example.com",
            "full_name": "Bob Wilson",
            "hashed_password": get_password_hash("password123"),
            "disabled": False
        },
        {
            "username": "alice_brown",
            "email": "alice@example.com",
            "full_name": "Alice Brown",
            "hashed_password": get_password_hash("password123"),
            "disabled": False
        },
        {
            "username": "charlie_davis",
            "email": "charlie@example.com",
            "full_name": "Charlie Davis",
            "hashed_password": get_password_hash("password123"),
            "disabled": False
        }
    ]
    
    for user in dummy_users:
        # Check if user already exists
        existing_user = users_collection.find_one({"username": user["username"]})
        if not existing_user:
            users_collection.insert_one(user)
            print(f"Created user: {user['username']}")

# Create dummy users on startup
@app.on_event("startup")
async def startup_event():
    create_dummy_users()
    print("Application started. Dummy users created.")


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - authenticate user and return JWT token.
    
    Test credentials:
    - Username: john_doe, Password: password123
    - Username: jane_smith, Password: password123
    - Username: bob_wilson, Password: password123
    - Username: alice_brown, Password: password123
    - Username: charlie_davis, Password: password123
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current logged-in user information"""
    return current_user


@app.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint - BUGGY: Claims to log user out but doesn't actually invalidate the token!
    
    BUG: This endpoint returns a success message, but the JWT token remains valid
    and can still be used to access protected endpoints until it expires.
    There's no session tracking in the database to invalidate tokens.
    """
    # BUG: We're not actually doing anything here!
    # The token is still valid and can be used
    # There's no session management in the database
    return {
        "message": "Logged out successfully",
        "detail": "Your session has been terminated"
    }
    # BUG: The above message is misleading - the token still works!


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file and store it in the data folder.
    Requires authentication.
    Returns the file ID and filename.
    """
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Get original filename
        original_filename = file.filename
        
        # Create file path with ID to avoid naming conflicts
        file_extension = Path(original_filename).suffix
        stored_filename = f"{file_id}{file_extension}"
        file_path = DATA_FOLDER / stored_filename
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store metadata in MongoDB
        file_document = {
            "_id": file_id,
            "filename": original_filename,
            "stored_filename": stored_filename,
            "size": len(content),
            "uploaded_by": current_user.username,
            "uploaded_at": datetime.now().isoformat()
        }
        files_collection.insert_one(file_document)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "file_id": file_id,
                "filename": original_filename,
                "uploaded_by": current_user.username
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/get_files")
async def get_files(current_user: User = Depends(get_current_active_user)) -> List[Dict]:
    """
    Get all uploaded files with their IDs and filenames.
    Requires authentication.
    """
    try:
        files = [
            {
                "file_id": file["_id"],
                "filename": file["filename"],
                "uploaded_by": file.get("uploaded_by", "unknown"),
                "uploaded_at": file.get("uploaded_at", "unknown")
            }
            for file in files_collection.find({})
        ]
        
        return files
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "File Upload API with Authentication",
        "endpoints": {
            "/login": "POST - Login and get access token",
            "/logout": "POST - Logout (requires authentication) - ⚠️ BUGGY",
            "/users/me": "GET - Get current user info (requires authentication)",
            "/upload": "POST - Upload a file (requires authentication)",
            "/get_files": "GET - Get all uploaded files (requires authentication)",
            "/docs": "GET - OpenAPI documentation"
        },
        "test_users": [
            {"username": "john_doe", "password": "password123"},
            {"username": "jane_smith", "password": "password123"},
            {"username": "bob_wilson", "password": "password123"},
            {"username": "alice_brown", "password": "password123"},
            {"username": "charlie_davis", "password": "password123"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

