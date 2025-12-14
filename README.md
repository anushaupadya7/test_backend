# FastAPI File Upload Project with Authentication

A FastAPI project with JWT authentication, file upload and retrieval endpoints, using MongoDB Atlas for data storage.

## Features

- 🔐 JWT-based authentication
- 👥 User login system with 5 pre-created dummy users
- 📤 Upload files via `/upload` endpoint (requires authentication)
- 📋 Retrieve list of uploaded files via `/get_files` endpoint (requires authentication)
- 💾 Files stored in `data` folder with unique IDs
- 🗄️ File metadata and users stored in MongoDB Atlas

## Prerequisites

- Python 3.7+
- MongoDB Atlas account with connection string

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MongoDB:
   - For local MongoDB: Make sure MongoDB is running on `mongodb://localhost:27017/`
   - For MongoDB Atlas or remote: Get your connection string

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update `MONGODB_URL` with your MongoDB connection string
   - Update `DB_NAME` if you want a different database name

```bash
cp .env.example .env
```

## Running the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Dummy Users (Pre-created)

The application automatically creates 5 test users on startup:

| Username | Password | Full Name |
|----------|----------|-----------|
| john_doe | password123 | John Doe |
| jane_smith | password123 | Jane Smith |
| bob_wilson | password123 | Bob Wilson |
| alice_brown | password123 | Alice Brown |
| charlie_davis | password123 | Charlie Davis |

## API Endpoints

### 1. Login (Get Access Token)
- **Endpoint**: `POST /login`
- **Description**: Authenticate and receive JWT access token
- **Request**: Form data with username and password
- **Response**: 
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Get Current User
- **Endpoint**: `GET /users/me`
- **Description**: Get information about the currently logged-in user
- **Authentication**: Required (Bearer token)
- **Response**: 
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "disabled": false
}
```

### 3. Upload File
- **Endpoint**: `POST /upload`
- **Description**: Upload a file and store it in the data folder
- **Authentication**: Required (Bearer token)
- **Request**: Multipart form data with file
- **Response**: 
```json
{
  "message": "File uploaded successfully",
  "file_id": "uuid-here",
  "filename": "original-filename.ext",
  "uploaded_by": "john_doe"
}
```

### 4. Get Files
- **Endpoint**: `GET /get_files`
- **Description**: Get all uploaded files with their IDs and filenames
- **Authentication**: Required (Bearer token)
- **Response**: 
```json
[
  {
    "file_id": "uuid-1",
    "filename": "file1.txt",
    "uploaded_by": "john_doe",
    "uploaded_at": "2025-12-15T10:30:00"
  }
]
```

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs` (Recommended for testing)
- **ReDoc**: `http://localhost:8000/redoc`

## Usage Guide

### Step 1: Login
1. Go to `http://localhost:8000/docs`
2. Click on `/login` endpoint
3. Click "Try it out"
4. Enter:
   - **username**: `john_doe`
   - **password**: `password123`
5. Click "Execute"
6. Copy the `access_token` from the response

### Step 2: Authorize
1. Click the "Authorize" button at the top of the page
2. Paste the token in the format: `Bearer <your_token>`
3. Click "Authorize"

### Step 3: Upload Files or Get Files
Now you can use the `/upload` and `/get_files` endpoints!

## MongoDB Atlas Setup

Your MongoDB connection is configured with:
- **Database Name**: `test_backend`
- **Collection Name**: `test_backend` (for files)
- **Collection Name**: `users` (for user accounts)

To view your data in MongoDB Compass:
1. Open MongoDB Compass
2. Connect using: `mongodb+srv://<username>:<password>@cluster0.temgbde.mongodb.net/`
3. Navigate to `test_backend` database
4. View `test_backend` collection (files) and `users` collection

