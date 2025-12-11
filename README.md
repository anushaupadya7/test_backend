# FastAPI File Upload Project

A simple FastAPI project with file upload and retrieval endpoints, using MongoDB for metadata storage.

## Features

- Upload files via `/upload` endpoint
- Retrieve list of uploaded files via `/get_files` endpoint
- Files stored in `data` folder with unique IDs
- File metadata stored in MongoDB

## Prerequisites

- Python 3.7+
- MongoDB installed and running locally, or a MongoDB connection string (e.g., MongoDB Atlas)

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

## API Endpoints

### 1. Upload File
- **Endpoint**: `POST /upload`
- **Description**: Upload a file and store it in the data folder
- **Request**: Multipart form data with file
- **Response**: 
```json
{
  "message": "File uploaded successfully",
  "file_id": "uuid-here",
  "filename": "original-filename.ext"
}
```

### 2. Get Files
- **Endpoint**: `GET /get_files`
- **Description**: Get all uploaded files with their IDs and filenames
- **Response**: 
```json
[
  {
    "file_id": "uuid-1",
    "filename": "file1.txt"
  },
  {
    "file_id": "uuid-2",
    "filename": "file2.pdf"
  }
]
```

## Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing with cURL

Upload a file:
```bash
curl -X POST "http://localhost:8000/upload" -F "file=@/path/to/your/file.txt"
```

Get all files:
```bash
curl -X GET "http://localhost:8000/get_files"
```
