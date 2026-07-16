from google.oauth2 import service_account
from googleapiclient.discovery import build
import time
from agent.logger import setup_logger

logger = setup_logger("SheetReader")

class SheetReader:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def __init__(self, service_account_file: str):
        try:
            self.creds = service_account.Credentials.from_service_account_file(
                service_account_file, scopes=self.SCOPES)
            self.service = build('sheets', 'v4', credentials=self.creds)
        except Exception as e:
            logger.error(f"Google Sheets API connection failed: {e}")
            raise

    def read_sheet(self, spreadsheet_id: str, range_name: str = 'Sheet1') -> list:
        """Read all rows from the specified spreadsheet."""
        for attempt in range(3):
            try:
                sheet = self.service.spreadsheets()
                # Get all data, you could query specifically but getting all is safe for small daily sheets
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
                values = result.get('values', [])
                if not values:
                    logger.warning(f"Spreadsheet {spreadsheet_id} is empty.")
                return values
            except Exception as e:
                logger.error(f"Google Sheets API error (Attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)
        return []

    def get_sheet_names(self, spreadsheet_id: str) -> list:
        # Get sheet metadata first to find actual range names
        try:
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            return [sheet.get("properties", {}).get("title", 'Sheet1') for sheet in sheets]
        except Exception as e:
            logger.error(f"Failed to fetch sheet metadata: {e}")
            return ['Sheet1']
