import re
from datetime import datetime

import pandas as pd
import streamlit as st

from agent.ai_email_generator import AIEmailGenerator
from agent.attendance_calculator import AttendanceCalculator
from agent.attendance_processor import AttendanceProcessor
from agent.drive_scanner import DriveScanner
from agent.email_sender import EmailSender
from agent.security import validate_email
from agent.sheet_reader import SheetReader
from agent.utils import get_current_month_str, get_today_date_str
from config.config import Config
from config.constants import Settings


st.set_page_config(
    page_title="Attendance Email AI Agent",
    page_icon="🤖",
    layout="wide",
)


def load_css() -> None:
    with open("assets/style.css", "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def extract_spreadsheet_id(sheet_url: str) -> str:
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
    if match:
        return match.group(1)

    match = re.search(r"id=([a-zA-Z0-9-_]+)", sheet_url)
    if match:
        return match.group(1)

    if not sheet_url.startswith("http"):
        return sheet_url.strip()

    raise ValueError("Invalid Google Sheet URL.")


def read_student_rows(rows: list[list[str]]) -> list[dict]:
    records = []
    if not rows:
        return records

    header_row_idx = Settings.SUBJECT_ROW_INDEX
    for idx, row in enumerate(rows):
        if any("Email" in str(cell) or "Roll No" in str(cell) for cell in row):
            header_row_idx = idx
            break

    for row in rows[header_row_idx + 1:]:
        if len(row) <= Settings.EMAIL_COL:
            continue

        roll_no = row[Settings.ROLL_NO_COL].strip() if len(row) > Settings.ROLL_NO_COL else ""
        name = row[Settings.NAME_COL].strip() if len(row) > Settings.NAME_COL else ""
        email = row[Settings.EMAIL_COL].strip() if len(row) > Settings.EMAIL_COL else ""

        if not name and not email:
            continue

        records.append(
            {
                "Roll Number": roll_no,
                "Student Name": name,
                "Email": email,
            }
        )

    return records


def build_preview_dataframe(rows: list[list[str]], absent_students: dict) -> pd.DataFrame:
    all_students = read_student_rows(rows)
    preview = []

    absent_lookup = {}
    for email, info in absent_students.items():
        absent_lookup[email] = {
            "subjects": ", ".join([lecture["subject"] for lecture in info["absent_lectures"]]),
            "status": "Pending",
        }

    for student in all_students:
        email = student["Email"]
        is_absent = email in absent_lookup
        preview.append(
            {
                "Roll Number": student["Roll Number"],
                "Student Name": student["Student Name"],
                "Email": email,
                "Attendance Status": "Absent" if is_absent else "Present",
                "Absent Subjects": absent_lookup[email]["subjects"] if is_absent else "-",
                "Email Status": absent_lookup[email]["status"] if is_absent else "-",
            }
        )

    return pd.DataFrame(preview)


def scan_sheet(sheet_url: str) -> dict:
    cfg = Config.load()
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    sheet_reader = SheetReader(cfg["service_account_file"])
    sheet_names = sheet_reader.get_sheet_names(spreadsheet_id)
    if not sheet_names:
        raise ValueError("No sheets found in the spreadsheet.")

    target_sheet = sheet_names[0]
    rows = sheet_reader.read_sheet(spreadsheet_id, target_sheet)
    if not rows:
        raise ValueError("The spreadsheet is empty or could not be read.")

    processor = AttendanceProcessor(rows)
    absent_students = processor.get_absent_students()
    preview_df = build_preview_dataframe(rows, absent_students)

    monthly_percentages = {}
    try:
        drive_scanner = DriveScanner(cfg["service_account_file"], cfg["google_drive_folder_id"])
        calculator = AttendanceCalculator(drive_scanner, sheet_reader)
        monthly_percentages = calculator.calculate_monthly_percentage(get_current_month_str())
    except Exception:
        monthly_percentages = {}

    return {
        "cfg": cfg,
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": target_sheet,
        "rows": rows,
        "absent_students": absent_students,
        "preview_df": preview_df,
        "monthly_percentages": monthly_percentages,
    }


def send_emails(scan_result: dict) -> tuple[pd.DataFrame, list[str], int]:
    cfg = scan_result["cfg"]
    absent_students = scan_result["absent_students"]
    monthly_percentages = scan_result["monthly_percentages"]
    today_date = get_today_date_str(Settings.DATE_FORMAT)

    email_generator = AIEmailGenerator(cfg["groq_api_key"], cfg["groq_model"])
    email_sender = EmailSender(cfg["email_address"], cfg["email_password"])

    logs = []
    sent_count = 0
    status_by_email = {}

    for email_addr, student_info in absent_students.items():
        if not validate_email(email_addr):
            logs.append(f"Skipped invalid email: {email_addr}")
            status_by_email[email_addr] = "Invalid Email"
            continue

        monthly_pct = monthly_percentages.get(email_addr, 0)
        email_content = email_generator.generate_email_content(student_info, today_date, monthly_pct)
        subject = f"Attendance Alert | {today_date}"
        email_sender.send_email(email_addr, subject, email_content)
        logs.append(f"Email sent to {student_info['name']} ({email_addr})")
        status_by_email[email_addr] = "Sent"
        sent_count += 1

    preview_df = scan_result["preview_df"].copy()
    if not preview_df.empty:
        preview_df["Email Status"] = preview_df.apply(
            lambda row: status_by_email.get(row["Email"], row["Email Status"]),
            axis=1,
        )

    return preview_df, logs, sent_count


def build_email_preview(scan_result: dict, selected_email: str) -> tuple[str, str]:
    absent_students = scan_result["absent_students"]
    monthly_percentages = scan_result["monthly_percentages"]
    today_date = get_today_date_str(Settings.DATE_FORMAT)

    if selected_email not in absent_students:
        return "Attendance Alert Preview", "No absent student selected."

    student_info = absent_students[selected_email]
    lectures = "\n".join(
        [f"- {lecture['subject']} ({lecture['timing']})" for lecture in student_info["absent_lectures"]]
    )
    monthly_pct = monthly_percentages.get(selected_email, 0)
    subject = f"Attendance Alert | {today_date}"
    body = (
        f"Dear {student_info['name']},\n\n"
        f"You were marked absent on {today_date}.\n\n"
        f"Absent Lectures:\n{lectures}\n\n"
        f"Monthly Attendance: {monthly_pct}%\n\n"
        "If this is incorrect, please contact your subject teacher.\n\n"
        "Regards,\nAttendance Email AI Agent"
    )
    return subject, body


def render_header() -> None:
    st.markdown(
        f"""
        <div class="app-shell">
            <div>
                <div class="mini-label">Attendance Automation</div>
                <h1>🤖 Attendance Email AI Agent</h1>
                <p>Paste a Google Sheet URL, scan the students, and send attendance emails.</p>
            </div>
            <div class="header-date">{datetime.now().strftime("%d %b %Y")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_cards(preview_df: pd.DataFrame) -> None:
    total_students = len(preview_df)
    absent_students = int((preview_df["Attendance Status"] == "Absent").sum()) if not preview_df.empty else 0
    sent_emails = int((preview_df["Email Status"] == "Sent").sum()) if not preview_df.empty else 0
    pending_emails = int((preview_df["Email Status"] == "Pending").sum()) if not preview_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Absent Students", absent_students)
    with col3:
        st.metric("Emails Sent", sent_emails)
    with col4:
        st.metric("Pending Emails", pending_emails)


def render_interactive_table(preview_df: pd.DataFrame) -> pd.DataFrame:
    toolbar_col1, toolbar_col2 = st.columns([1.3, 0.7])
    with toolbar_col1:
        search_text = st.text_input("Search Students", placeholder="Search by name, roll number, or email")
    with toolbar_col2:
        status_filter = st.selectbox("Filter Status", ["All", "Absent", "Present", "Sent", "Pending", "Invalid Email"])

    filtered_df = preview_df.copy()
    if search_text:
        query = search_text.lower()
        filtered_df = filtered_df[
            filtered_df.apply(lambda row: query in " ".join(map(str, row)).lower(), axis=1)
        ]

    if status_filter == "Absent":
        filtered_df = filtered_df[filtered_df["Attendance Status"] == "Absent"]
    elif status_filter == "Present":
        filtered_df = filtered_df[filtered_df["Attendance Status"] == "Present"]
    elif status_filter in {"Sent", "Pending", "Invalid Email"}:
        filtered_df = filtered_df[filtered_df["Email Status"] == status_filter]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=420,
    )
    return filtered_df


def main() -> None:
    load_css()
    render_header()

    if "scan_result" not in st.session_state:
        st.session_state["scan_result"] = None
    if "preview_df" not in st.session_state:
        st.session_state["preview_df"] = pd.DataFrame()
    if "logs" not in st.session_state:
        st.session_state["logs"] = []
    if "selected_email" not in st.session_state:
        st.session_state["selected_email"] = ""

    sheet_url = st.text_input(
        "Google Sheet URL",
        placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit#gid=0",
    )
    action_col1, action_col2 = st.columns([1, 1])

    with action_col1:
        if st.button("Scan Students", use_container_width=True):
            try:
                with st.status("Scanning spreadsheet...", expanded=True) as status_box:
                    status_box.write("Loading configuration")
                    result = scan_sheet(sheet_url)
                    status_box.write(f"Reading sheet: {result['sheet_name']}")
                    status_box.write("Attendance scan completed")
                    status_box.update(label="Scan complete", state="complete")

                st.session_state["scan_result"] = result
                st.session_state["preview_df"] = result["preview_df"]
                st.session_state["logs"] = [
                    f"Sheet scanned successfully: {result['sheet_name']}",
                    f"Students found: {len(result['preview_df'])}",
                    f"Absent students: {len(result['absent_students'])}",
                ]
                st.toast("Students scanned successfully", icon="✅")
            except Exception as exc:
                st.error(str(exc))

    with action_col2:
        send_disabled = st.session_state["scan_result"] is None
        if st.button("Send Emails", use_container_width=True, disabled=send_disabled):
            try:
                with st.status("Sending emails...", expanded=True) as status_box:
                    status_box.write("Generating email content")
                    updated_df, logs, sent_count = send_emails(st.session_state["scan_result"])
                    status_box.write("Delivering emails")
                    status_box.update(label="Emails sent", state="complete")

                st.session_state["preview_df"] = updated_df
                st.session_state["logs"].extend(logs)
                st.toast(f"{sent_count} emails sent", icon="📨")
            except Exception as exc:
                st.error(str(exc))
    if not st.session_state["preview_df"].empty:
        render_summary_cards(st.session_state["preview_df"])

        st.markdown("### Student Scan Result")
        render_interactive_table(st.session_state["preview_df"])
        progress_value = int(
            (
                (st.session_state["preview_df"]["Email Status"] == "Sent").sum()
                / max((st.session_state["preview_df"]["Attendance Status"] == "Absent").sum(), 1)
            ) * 100
        )
        st.progress(progress_value, text=f"Email delivery progress: {progress_value}%")

        absent_df = st.session_state["preview_df"][
            st.session_state["preview_df"]["Attendance Status"] == "Absent"
        ]
        if not absent_df.empty and st.session_state["scan_result"] is not None:
            st.markdown("### Email Preview")
            options = absent_df["Email"].tolist()
            default_index = 0
            if st.session_state["selected_email"] in options:
                default_index = options.index(st.session_state["selected_email"])

            st.session_state["selected_email"] = st.selectbox(
                "Select Student",
                options,
                index=default_index,
                format_func=lambda email: f"{absent_df[absent_df['Email'] == email]['Student Name'].iloc[0]} - {email}",
            )
            preview_subject, preview_body = build_email_preview(
                st.session_state["scan_result"],
                st.session_state["selected_email"],
            )
            st.markdown(f"**Subject:** {preview_subject}")
            st.code(preview_body, language="text")

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Execution Logs")
    st.code(
        "\n".join(st.session_state["logs"]) if st.session_state["logs"] else "Waiting for scan...",
        language="text",
    )
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
