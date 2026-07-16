# 🤖 Attendance Email AI Agent

An AI-powered automation system that scans attendance records stored in Google Sheets, identifies absent students, generates personalized attendance notification emails using the Groq LLM, and sends a single email to each absent student automatically.

The project uses Google Drive API, Google Sheets API, Groq API, and SMTP Email Service to automate attendance notifications without manual intervention.

---

# 📌 Features

- Automatically scans a Google Drive folder for today's attendance spreadsheet.
- Uses the current system date to identify the correct attendance file.
- Reads attendance directly from Google Sheets.
- Supports Google Service Account authentication.
- Uses Google Drive API and Google Sheets API.
- Identifies students who are absent.
- Combines multiple absent lectures into a single email.
- Generates professional emails using the Groq LLM.
- Sends only one email per absent student.
- Calculates monthly attendance dynamically by reading attendance spreadsheets for the current month.
- Maintains detailed execution logs.
- Secure configuration using environment variables.
- Modular and scalable architecture.
- Production-ready Python project.

---

# 🏗️ System Architecture

```text
                     Google Cloud Platform
                              │
                              ▼
                   Google Service Account
                              │
                              ▼
                     Google Drive MCP
                              │
                              ▼
                     Google Drive API
                              │
                              ▼
                    Google Sheets API
                              │
                              ▼
                Attendance Email AI Agent
                              │
        ┌─────────────────────────────────────────┐
        │                                         │
        ▼                                         ▼
 Drive Scanner                         Attendance Processor
        │                                         │
        └─────────────────┬───────────────────────┘
                          ▼
                 Groq AI Email Generator
                          │
                          ▼
                  SMTP Email Service
                          │
                          ▼
                 Student Email Inbox
```

---

# ⚙️ Technologies Used

- Python 3.11+
- Google Drive API
- Google Sheets API
- Google Drive MCP
- Google Service Account
- Groq API
- SMTP
- Pandas
- gspread
- python-dotenv
- Google Authentication
- Logging

---

# 📁 Project Structure

```text
Attendance-Email-AI-Agent/

│
├── agent/
│   ├── drive_scanner.py
│   ├── sheet_reader.py
│   ├── attendance_processor.py
│   ├── ai_email_generator.py
│   ├── email_sender.py
│   ├── validator.py
│   ├── logger.py
│   ├── prompts.py
│   ├── security.py
│   └── utils.py
│
├── config/
│   ├── config.py
│   └── constants.py
│
├── credentials/
│   └── service_account.json
│
├── templates/
│   ├── attendance_email.txt
│   ├── system_prompt.txt
│   └── email_subject.txt
│
├── logs/
│   └── attendance.log
│
├── tests/
│
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── LICENSE
├── main.py
└── run.py
```

---

# 📂 Google Drive Folder Structure

```text
Attendance Folder

│

├── 01-07-2026
├── 02-07-2026
├── 03-07-2026
├── 04-07-2026
└── ...
```

Each file inside the folder is a Google Spreadsheet.

The spreadsheet filename follows:

```
DD-MM-YYYY
```

Example:

```
15-07-2026
```

---

# 📊 Spreadsheet Format

Each spreadsheet stores attendance records.

| Roll No | Student Name | Email | 9:15–10:15 (AI)| 10:15–11:15 (DL) | 11:30–12:30 (DBMS)| 12:30–1:30 (DSA) |
|----------|--------------|--------|------------|-------------|-------------|-------------|
| 101 | Rahul | rahul@email.com | P | A | P | A |

Where:

- **P = Present**
- **A = Absent**

The first row represents lecture timings.

The second row represents subject names.

The AI Agent automatically maps lecture timings to subject names.

---

# 🤖 AI Agent Workflow

1. Read the current system date.
2. Connect to Google Drive.
3. Scan the attendance folder.
4. Locate today's attendance spreadsheet.
5. Read attendance from Google Sheets.
6. Identify absent students.
7. Group multiple absent lectures for each student.
8. Calculate monthly attendance percentage.
9. Generate personalized attendance emails using Groq.
10. Send one email per absent student.
11. Save execution logs.

---

# 📧 Email Notification

Every student receives only one email regardless of the number of absent lectures.

The email includes:

- Student Name
- Roll Number
- Attendance Date
- Absent Subjects
- Lecture Timings
- Monthly Attendance Percentage
- Official Attendance Notice

---

# 📈 API Monitoring Dashboard

The Attendance Email AI Agent continuously monitors the health and performance of the Google Cloud services used during execution.


<img width="1860" height="592" alt="image" src="https://github.com/user-attachments/assets/6cd40862-4476-42ea-a6b4-0fe5235f6fbd" />

The monitoring dashboard provides real-time insights into the enabled Google Cloud APIs used by the project.
---

# 📧 AI Generated Email

The AI Agent generates a personalized attendance notification using the Groq LLM and sends a single email to each absent student, even if they are absent in multiple lectures.

<img width="687" height="626" alt="image" src="https://github.com/user-attachments/assets/f3aebb2c-0cb1-4716-9211-244e294f7e53" />


---

# 🔐 Security

The project stores all sensitive information using environment variables.

Example:

```env
GROQ_MODEL=
GOOGLE_DRIVE_FOLDER_URL=
SERVICE_ACCOUNT_FILE=
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=
GORQ_API_KEY=
```

Credentials are never hardcoded inside the source code.

---

# 📜 Logging

Execution logs are stored in:

```
logs/attendance.log
```

The following events are recorded:

- Agent Started
- Google Drive Connected
- Spreadsheet Found
- Attendance Loaded
- Attendance Processed
- Email Generated
- Email Sent
- Errors
- Execution Completed

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/your-username/Attendance-Email-AI-Agent.git
```

Move inside the project

```bash
cd Attendance-Email-AI-Agent
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Project

```bash
python main.py
```

---

# 📌 Future Improvements

- SMS notifications
- WhatsApp attendance alerts
- Faculty dashboard
- Student attendance analytics
- Scheduled automatic execution
- Cloud deployment
- Attendance report generation
- AI-based attendance insights

---

# 📄 License

This project is licensed under the MIT License.

---


