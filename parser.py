import json
import re

class ReminderOutputParser:
    def parse(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return self._regex_parse(text)
    
    def _regex_parse(self, text: str) -> dict:
        patterns = {
            "time": r"\b(\d{1,2}:\d{2} [AP]M)\b",
            "task": r"task[\"']?:[\"']?(.+?)[\"']?(?=,|$)",
            "date": r"\b(\d{4}-\d{2}-\d{2})\b"
        }
        return {k: re.search(v, text).group(1) for k,v in patterns.items() if re.search(v, text)}