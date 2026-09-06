import os
import logging
from typing import List, Dict, Any
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class FileStorageService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"Initialized FileStorageService with base_dir: {self.base_dir}")

    def get_file_path(self, filename: str, subdir: str) -> str:
        """Get full path."""
        target_dir = os.path.join(self.base_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)
        return os.path.join(target_dir, filename)

    def save_upload(self, file: UploadFile, subdir: str) -> str:
        """Save uploaded file, return full path."""
        file_path = self.get_file_path(file.filename, subdir)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        logger.info(f"Saved uploaded file to {file_path}")
        return file_path

    def save_bytes(self, data: bytes, filename: str, subdir: str) -> str:
        """Save raw bytes."""
        file_path = self.get_file_path(filename, subdir)
        with open(file_path, "wb") as f:
            f.write(data)
        logger.info(f"Saved bytes to {file_path}")
        return file_path

    def delete_file(self, file_path: str):
        """Delete a file."""
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file {file_path}")
        else:
            logger.warning(f"File {file_path} not found for deletion")

    def list_files(self, subdir: str) -> List[Dict[str, Any]]:
        """List files in a subdirectory."""
        target_dir = os.path.join(self.base_dir, subdir)
        if not os.path.exists(target_dir):
            return []
            
        files = []
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "path": file_path,
                    "size": stat.st_size,
                    "modified_time": stat.st_mtime
                })
        return files
