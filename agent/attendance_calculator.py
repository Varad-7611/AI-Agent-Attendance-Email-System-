from config.constants import Settings
from agent.logger import setup_logger

logger = setup_logger("AttendanceCalculator")

class AttendanceCalculator:
    def __init__(self, drive_scanner, sheet_reader):
        self.drive_scanner = drive_scanner
        self.sheet_reader = sheet_reader
        
    def calculate_monthly_percentage(self, month_str: str) -> dict:
        """
        Calculates monthly attendance percentage for all students.
        Does not use a database. Scans the Google Drive folder.
        """
        logger.info(f"Calculating Attendance for month {month_str}")
        files = self.drive_scanner.get_monthly_files(month_str)
        
        student_stats = {} # { "email": {"present": X, "total": Y} }
        
        for file in files:
            file_id = file.get("id")
            sheet_names = self.sheet_reader.get_sheet_names(file_id)
            for sheet_name in sheet_names:
                rows = self.sheet_reader.read_sheet(file_id, sheet_name)
                
                if not rows or len(rows) <= Settings.DATA_START_ROW_INDEX:
                    continue
                    
                header_timings = rows[Settings.TIMING_ROW_INDEX]
                # Calculate number of valid lectures on this sheet day
                num_lectures = len(header_timings) - Settings.LECTURE_START_COL
                if num_lectures <= 0:
                    continue
                    
                for row_index in range(Settings.DATA_START_ROW_INDEX, len(rows)):
                    row = rows[row_index]
                    if len(row) <= Settings.EMAIL_COL:
                        continue
                        
                    email = row[Settings.EMAIL_COL].strip()
                    if not email:
                        continue
                        
                    if email not in student_stats:
                        student_stats[email] = {"present": 0, "total": 0}
                        
                    for i in range(num_lectures):
                        col_idx = Settings.LECTURE_START_COL + i
                        att = row[col_idx].strip().upper() if col_idx < len(row) else ""
                        
                        student_stats[email]["total"] += 1
                        if att == Settings.PRESENT_VALUE:
                            student_stats[email]["present"] += 1
                            
        # Calculate final percentages
        percentages = {}
        for email, stats in student_stats.items():
            if stats["total"] > 0:
                percentage = (stats["present"] / stats["total"]) * 100
                percentages[email] = round(percentage)
            else:
                percentages[email] = 0
                
        return percentages
