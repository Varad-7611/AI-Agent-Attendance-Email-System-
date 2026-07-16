import sys
sys.path.append('.')
from config.config import Config
from agent.drive_scanner import DriveScanner
from agent.sheet_reader import SheetReader
cfg = Config.load()
scanner = DriveScanner(cfg['service_account_file'], cfg['google_drive_folder_id'])
reader = SheetReader(cfg['service_account_file'])
q = f"'{scanner.folder_id}' in parents and name = '15/7/2026' and trashed=false"
res = scanner.service.files().list(q=q, fields='files(id, shortcutDetails)').execute()
file_id = res['files'][0]['shortcutDetails']['targetId']
rows = reader.read_sheet(file_id, '15/07/2026')
for idx, r in enumerate(rows):
    print(idx, r)
