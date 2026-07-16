import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time
from agent.logger import setup_logger

logger = setup_logger("DriveScanner")

class DriveScanner:
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    def __init__(self, service_account_file: str, folder_id: str):
        self.folder_id = folder_id
        try:
            self.creds = service_account.Credentials.from_service_account_file(
                service_account_file, scopes=self.SCOPES)
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("Connected Google Drive")
        except Exception as e:
            logger.error(f"Google Drive connection failed: {e}")
            raise

    def find_file_by_name(self, filename: str) -> str:
        """Searches for a specific file by name in the given folder."""
        logger.info(f"Scanning Folder {self.folder_id} for file: {filename}")
        query = f"'{self.folder_id}' in parents and name = '{filename}' and trashed = false"
        
        # Retry mechanism
        for attempt in range(3):
            try:
                results = self.service.files().list(q=query, fields="files(id, name, mimeType, shortcutDetails)").execute()
                items = results.get('files', [])
                if items:
                    item = items[0]
                    file_id = item['id']
                    if item.get('mimeType') == 'application/vnd.google-apps.shortcut':
                        file_id = item.get('shortcutDetails', {}).get('targetId', file_id)
                        logger.info(f"File {filename} is a shortcut pointing to target ID: {file_id}")
                    else:
                        logger.info(f"File {filename} found (ID: {file_id})")
                    return file_id
                
                logger.warning(f"File {filename} not found.")
                return None
            except Exception as e:
                logger.error(f"Error querying drive (Attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)
        return None

    def get_monthly_files(self, month_str: str) -> list:
        """Finds all spreadsheets for the current month."""
        query = f"'{self.folder_id}' in parents and name contains '{month_str}' and trashed = false"
        files = []
        page_token = None
        while True:
            try:
                results = self.service.files().list(
                    q=query, fields="nextPageToken, files(id, name)", pageToken=page_token).execute()
                files.extend(results.get('files', []))
                page_token = results.get('nextPageToken', None)
                if page_token is None:
                    break
            except Exception as e:
                logger.error(f"Error fetching monthly files: {e}")
                break
        return files
