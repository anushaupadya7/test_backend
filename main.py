from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from pathlib import Path
from typing import List, Dict

app = FastAPI(title="File Upload API")

# Create data folder if it doesn't exist
DATA_FOLDER = Path("data")
DATA_FOLDER.mkdir(exist_ok=True)

# Store file metadata (in production, use a database)
file_metadata = {}


@app.post("/uploa")
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
        
        # Store metadata
        file_metadata[file_id] = {
            "id": file_id,
            "filename": original_filename,
            "stored_filename": stored_filename,
            "size": len(content)
        }
        
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
                "file_id": file_id,
                "filename": metadata["filename"]
            }
            for file_id, metadata in file_metadata.items()
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
