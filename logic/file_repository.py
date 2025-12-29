import os
import shutil
import datetime

class FileRepository:
    BASE_DIR = os.path.join(os.getcwd(), "backend_data", "corpus")
    
    @staticmethod
    def _ensure_dir(category):
        path = os.path.join(FileRepository.BASE_DIR, category)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def save_upload(uploaded_file, category="general"):
        """
        Saves a Streamlit UploadedFile to the backend corpus.
        Returns the absolute path of the saved file.
        """
        if uploaded_file is None: return None
        
        try:
            target_dir = FileRepository._ensure_dir(category)
            # Timestamp to avoid collisions, but keep original name for context
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = f"{ts}_{uploaded_file.name}"
            target_path = os.path.join(target_dir, safe_name)
            
            with open(target_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            return target_path
        except Exception as e:
            print(f"⚠️ Repo Save Error: {e}")
            return None

    @staticmethod
    def save_output(content_bytes, original_name, category="outputs"):
        """
        Saves generated content (bytes) to match original filename.
        """
        try:
            target_dir = FileRepository._ensure_dir(category)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = f"{ts}_{original_name}"
            target_path = os.path.join(target_dir, safe_name)
            
            with open(target_path, "wb") as f:
                f.write(content_bytes)
            return target_path
        except Exception as e:
            return None

    @staticmethod
    def delete_file(filepath):
        """
        Securely deletes the file from the filesystem.
        """
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ PRIVACY: Deleted {os.path.basename(filepath)}")
                return True
        except Exception as e:
            print(f"⚠️ Deletion Failed: {e}")
            return False
