import sys
from config.config import Config
from config.constants import Settings
from agent.logger import setup_logger
from agent.utils import get_today_date_str, get_current_month_str
from agent.drive_scanner import DriveScanner
from agent.sheet_reader import SheetReader
from agent.attendance_processor import AttendanceProcessor
from agent.attendance_calculator import AttendanceCalculator
from agent.ai_email_generator import AIEmailGenerator
from agent.email_sender import EmailSender
from agent.security import validate_email

logger = setup_logger("Main")

def main():
    logger.info("Agent Started")
    
    try:
        cfg = Config.load()
    except Exception as e:
        logger.error(f"Configuration Initialization failed: {e}")
        sys.exit(1)
        
    try:
        # Initialize components
        drive_scanner = DriveScanner(cfg['service_account_file'], cfg['google_drive_folder_id'])
        sheet_reader = SheetReader(cfg['service_account_file'])
        
        # 1. Connected Google Drive / Scanning folder
        today_date = get_today_date_str(Settings.DATE_FORMAT)
        from datetime import datetime
        now = datetime.now()
        today_filename = f"{now.day}/{now.month}/{now.year}"
        
        today_file_id = drive_scanner.find_file_by_name(today_filename)
        if not today_file_id:
            logger.warning(f"Spreadsheet '{today_filename}' missing or not found. Exiting gracefully.")
            logger.info("Execution Completed")
            sys.exit(0)
            
        logger.info(f"Spreadsheet '{today_filename}' Found")
        
        # 2. Reading Attendance
        sheet_names = sheet_reader.get_sheet_names(today_file_id)
        logger.info(f"Found sheets: {sheet_names}")
        
        # We will try to find a sheet matching today date, otherwise fallback to the first sheet
        target_sheet = sheet_names[0]
        # Example: Try to match "15/7" or something if needed, but for now just use the first sheet (which is often the newest).
        rows = sheet_reader.read_sheet(today_file_id, target_sheet)
        
        attendance_processor = AttendanceProcessor(rows)
        absent_students = attendance_processor.get_absent_students()
        
        if not absent_students:
            logger.info("No absent students found today.")
            logger.info("Execution Completed")
            sys.exit(0)
            
        # 3. Calculating Attendance (dynamically from Google Drive)
        calculator = AttendanceCalculator(drive_scanner, sheet_reader)
        monthly_percentages = calculator.calculate_monthly_percentage(get_current_month_str())
        
        # 4. Generating & Sending Email
        email_generator = AIEmailGenerator(cfg['groq_api_key'], cfg['groq_model'])
        email_sender = EmailSender(cfg['email_address'], cfg['email_password'])
        
        for email_addr, student_info in absent_students.items():
            if not validate_email(email_addr):
                logger.error(f"Invalid email: {email_addr}. Skipping.")
                continue
                
            try:
                monthly_pct = monthly_percentages.get(email_addr, 0)
                
                logger.info(f"Generating Email for {student_info['name']}")
                email_content = email_generator.generate_email_content(student_info, today_date, monthly_pct)
                
                subject = f"Attendance Alert | {today_date}"
                
                # Send strictly ONE email per student containing all info
                email_sender.send_email(email_addr, subject, email_content)
                logger.info(f"Email Sent to {student_info['name']}")
                
            except Exception as e:
                logger.error(f"Failed to process email for {student_info['name']}: {e}")
                # We log and continue so one failure doesn't stop others
        
        logger.info("Execution Completed")
        
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
