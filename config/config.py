import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    @staticmethod
    def get_env_var(var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Missing environment variable: {var_name}")
        return value

    @staticmethod
    def get_google_drive_folder_id() -> str:
        url = Config.get_env_var("GOOGLE_DRIVE_FOLDER_URL")
        # Extract ID from a URL like https://drive.google.com/drive/folders/XXXYYY
        match = re.search(r"folders/([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(1)
        # Direct ID in URL fallback if format differs
        if "id=" in url:
            match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
            if match:
                return match.group(1)
        # Assume it's an ID if no match and it's not a url
        if not url.startswith("http"):
            return url
        raise ValueError("Could not extract Google Drive Folder ID from URL.")

    @classmethod
    def load(cls):
        service_account_file = os.getenv("SERVICE_ACCOUNT_FILE", "credentials/service_account.json")
        if not os.path.exists(service_account_file):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cred_dir = os.path.join(base_dir, 'credentials')
            if os.path.exists(cred_dir):
                jsons = [f for f in os.listdir(cred_dir) if f.endswith('.json')]
                if jsons:
                    service_account_file = os.path.join(cred_dir, jsons[0])
                    
        return {
            "email_address": cls.get_env_var("SMTP_USERNAME"),
            "email_password": cls.get_env_var("SMTP_PASSWORD"),
            "groq_api_key": cls.get_env_var("GORQ_API_KEY"),
            "groq_model": cls.get_env_var("GROQ_MODEL"),
            "google_drive_folder_id": cls.get_google_drive_folder_id(),
            "service_account_file": service_account_file,
        }
