import json
import re
from datetime import datetime

class ReminderOutputParser:
    def parse(self, text):
        # Flexible patterns for time, task, and date
        time_pattern = r"Time: (\d{1,2}(?::\d{2})?\s*[ap]m|\d{1,2}(?::\d{2})?)"
        task_pattern = r"Task: (.+?)(?=\s*(?:Time:|Date:|$))"
        date_pattern = r"Date: (\d{4}-\d{2}-\d{2}|\d{1,2}(?:st|nd|rd|th)?\s*\w+)"
        
        # Extract time, task, and date
        time = re.search(time_pattern, text, re.IGNORECASE)
        task = re.search(task_pattern, text, re.IGNORECASE)
        date = re.search(date_pattern, text, re.IGNORECASE)
        
        # Format extracted values
        time = time.group(1).strip() if time else None
        task = task.group(1).strip() if task else "Reminder"
        date = date.group(1).strip() if date else datetime.now().strftime("%Y-%m-%d")
        
        # Convert date to standard format (e.g., "25th December" -> "2023-12-25")
        if date and not re.match(r"\d{4}-\d{2}-\d{2}", date):
            current_year = datetime.now().year
            try:
                date = datetime.strptime(f"{date} {current_year}", "%dth %B %Y").strftime("%Y-%m-%d")
            except ValueError:
                try:
                    date = datetime.strptime(f"{date} {current_year}", "%d %B %Y").strftime("%Y-%m-%d")
                except ValueError:
                    date = datetime.now().strftime("%Y-%m-%d")
        
        # Create dictionary and convert to JSON
        result = {"time": time, "task": task, "date": date}
        return json.dumps(result)