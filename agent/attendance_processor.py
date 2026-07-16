from config.constants import Settings
from agent.logger import setup_logger

logger = setup_logger("AttendanceProcessor")

class AttendanceProcessor:
    def __init__(self, rows: list):
        self.rows = rows
        self.timings = []
        self.subjects = []
        self._parse_headers()

    def _parse_headers(self):
        """Extract lectures timings and subjects from the headers dynamically."""
        # Find the header row by looking for 'Roll No' or 'Email'
        header_row_idx = Settings.SUBJECT_ROW_INDEX
        for idx, row in enumerate(self.rows):
            if any("Email" in str(cell) or "Roll No" in str(cell) for cell in row):
                header_row_idx = idx
                break
                
        if len(self.rows) <= header_row_idx:
            return
            
        header_subjects = self.rows[header_row_idx]
        # if the row above isn't empty, use it for timings, otherwise fallback to the subject row itself
        if header_row_idx > 0 and self.rows[header_row_idx - 1]:
            header_timings = self.rows[header_row_idx - 1]
        else:
            header_timings = header_subjects
            
        # Dynamically set DATA_START_ROW_INDEX
        self.data_start_idx = header_row_idx + 1
        
        # Determine number of lectures by looking at lengths starting from LECTURE_START_COL
        max_len = max(len(header_timings), len(header_subjects))
        
        for col_index in range(Settings.LECTURE_START_COL, max_len):
            timing = header_timings[col_index] if col_index < len(header_timings) else "Unknown Time"
            subject = header_subjects[col_index] if col_index < len(header_subjects) else "Unknown Subject"
            
            # Stop if empty (assuming no gaps in columns)
            if not timing.strip() and not subject.strip():
                break
                
            self.timings.append(timing.strip())
            self.subjects.append(subject.strip())
            
    def get_absent_students(self) -> dict:
        """
        Scans data rows and returns a dict mapping student emails to their absentee data.
        Returns format: 
        {
            "student@email.com": {
                "name": "Student Name",
                "roll_no": "Roll No",
                "absent_lectures": [ {"subject": "Math", "timing": "9:15"} ]
            }
        }
        """
        absent_data = {}
        data_start = getattr(self, 'data_start_idx', Settings.DATA_START_ROW_INDEX)
        if len(self.rows) <= data_start:
            return absent_data
            
        logger.info("Reading Attendance...")
            
        for row_index in range(data_start, len(self.rows)):
            row = self.rows[row_index]
            if not row or len(row) <= Settings.EMAIL_COL:
                continue
                
            roll_no = row[Settings.ROLL_NO_COL].strip()
            name = row[Settings.NAME_COL].strip()
            email = row[Settings.EMAIL_COL].strip()
            
            if not email:
                continue
                
            student_absent_lectures = []
            
            for i in range(len(self.timings)):
                col_index = Settings.LECTURE_START_COL + i
                attendance = row[col_index].strip().upper() if col_index < len(row) else ""
                
                if attendance == Settings.ABSENT_VALUE:
                    student_absent_lectures.append({
                        "subject": self.subjects[i],
                        "timing": self.timings[i]
                    })
                    
            if student_absent_lectures:
                absent_data[email] = {
                    "name": name,
                    "roll_no": roll_no,
                    "absent_lectures": student_absent_lectures
                }
                
        return absent_data
