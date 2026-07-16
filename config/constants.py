class Settings:
    DATE_FORMAT = "%d-%m-%Y"
    
    # Spreadsheet exact rows according to design
    TIMING_ROW_INDEX = 0
    SUBJECT_ROW_INDEX = 1
    DATA_START_ROW_INDEX = 2
    
    # Columns
    ROLL_NO_COL = 0
    NAME_COL = 1
    EMAIL_COL = 2
    LECTURE_START_COL = 3
    
    # Attendance values
    PRESENT_VALUE = "P"
    ABSENT_VALUE = "A"

class LogConfig:
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/attendance.log"
