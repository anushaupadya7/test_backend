from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from pathlib import Path
from typing import List, Dict
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="File Upload API")

# Create data folder if it doesn't exist
DATA_FOLDER = Path("data")
DATA_FOLDER.mkdir(exist_ok=True)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URL)
db = client[os.getenv("DB_NAME", "file_upload_db")]
files_collection = db["files"]


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and store it in the data folder.
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
            "size": len(content)
        }
        files_collection.insert_one(file_document)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "file_id": file_id,
                "filename": original_filename
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/get_files")
async def get_files() -> List[Dict[str, str]]:
    """
    Get all uploaded files with their IDs and filenames.
    """
    try:
        files = [
            {
                "file_id": file["_id"],
                "filename": file["filename"]
            }
            for file in files_collection.find({}, {"_id": 1, "filename": 1})
        ]
        
        return files
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "File Upload API",
        "endpoints": {
            "/upload": "POST - Upload a file",
            "/get_files": "GET - Get all uploaded files"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
