import os
from groq import Groq
from agent.logger import setup_logger
from agent.prompts import get_system_prompt
from agent.security import sanitize_llm_input
import datetime

logger = setup_logger("AIEmailGenerator")

class AIEmailGenerator:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("Groq API Key is not set.")
        # Ensure we don't accidentally pass an empty string
        # Groq client will throw if api_key is None OR empty
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate_email_content(self, student_info: dict, date_str: str, monthly_percentage: int) -> str:
        """Uses Groq to generate a polite email based on the student's absence."""
        logger.info(f"Generating Email for {student_info['name']}")
        
        # Construct raw data context
        absent_lectures_str = "\\n".join([f"• {l['subject']}\\n  {l['timing']}" for l in student_info['absent_lectures']])
        
        # Load local template for exact structure matching if we want strict formatting 
        # (Alternatively, let the LLM format it based on the strict system prompt)
        
        user_prompt = (
            f"Generate an attendance email for student {student_info['name']} (Roll No: {student_info['roll_no']}).\n"
            f"Date: {date_str}\n"
            f"Absent Lectures:\n{absent_lectures_str}\n"
            f"Monthly Attendance Percentage: {monthly_percentage}%\n"
            "Format the email EXACTLY as per the system prompt instructions."
        )
        
        user_prompt = sanitize_llm_input(user_prompt)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_completion_tokens=1024
            )
            content = chat_completion.choices[0].message.content.strip()
            # Strip markdown formatting if the LLM still returns it
            if content.startswith("```html"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            logger.info(f"Generated email format check: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"Groq API error for {student_info['name']}: {e}")
            raise
