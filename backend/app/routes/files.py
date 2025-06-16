import os
import uuid
import base64
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/api/files", tags=["files"])

# Allowed file types
ALLOWED_TYPES = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"],
    "video": ["video/mp4", "video/avi", "video/mov", "video/wmv", "video/flv"],
    "audio": ["audio/mp3", "audio/wav", "audio/aac", "audio/ogg"],
    "document": [
        "application/pdf", 
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain", 
        "application/json", 
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def is_allowed_file_type(content_type: str) -> bool:
    """Check if the file type is allowed"""
    for category, types in ALLOWED_TYPES.items():
        if content_type in types:
            return True
    return False


def get_file_category(content_type: str) -> str:
    """Get the category of the file"""
    for category, types in ALLOWED_TYPES.items():
        if content_type in types:
            return category
    return "unknown"


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file"""
    try:
        # Validate file type
        if not is_allowed_file_type(file.content_type):
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} is not allowed"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"File uploaded: {file.filename} -> {unique_filename}")
        
        return {
            "id": file_id,
            "filename": file.filename,
            "url": f"/api/files/{file_id}",
            "size": len(file_content),
            "type": file.content_type,
            "category": get_file_category(file.content_type)
        }
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files"""
    if len(files) > 10:  # Limit to 10 files per request
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request")
    
    results = []
    for file in files:
        try:
            result = await upload_file(file)
            results.append(result)
        except HTTPException as e:
            results.append({
                "filename": file.filename,
                "error": e.detail,
                "status_code": e.status_code
            })
    
    return {"files": results}


@router.get("/{file_id}")
async def get_file(file_id: str):
    """Get a file by ID"""
    try:
        # Find file with this ID
        for file_path in UPLOAD_DIR.glob(f"{file_id}.*"):
            if file_path.is_file():
                return FileResponse(
                    path=str(file_path),
                    filename=file_path.name,
                    media_type="application/octet-stream"
                )
        
        raise HTTPException(status_code=404, detail="File not found")
    
    except Exception as e:
        logger.error(f"Error retrieving file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete a file by ID"""
    try:
        # Find and delete file with this ID
        deleted = False
        for file_path in UPLOAD_DIR.glob(f"{file_id}.*"):
            if file_path.is_file():
                file_path.unlink()
                deleted = True
                logger.info(f"File deleted: {file_path.name}")
        
        if not deleted:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"message": "File deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@router.get("/")
async def list_files():
    """List all uploaded files"""
    try:
        files = []
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                file_id = file_path.stem
                files.append({
                    "id": file_id,
                    "filename": file_path.name,
                    "url": f"/api/files/{file_id}",
                    "size": stat.st_size,
                    "created_at": stat.st_ctime
                })
        
        return {"files": files}
    
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")