import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.schedule_url = os.getenv("SCHEDULE_URL")
        self.base_url = os.getenv("BASE_URL")
        self.keyword = os.getenv("KEYWORD")
        self.target_member = os.getenv("TARGET_MEMBER")
        self.weekday_conversion = {
            "MON": "月",
            "TUE": "火",
            "WED": "水",
            "THU": "木",
            "FRI": "金",
            "SAT": "土",
            "SUN": "日"
        }
        self.max_workers = 5
        self.request_timeout = 5
        self.retry_count = 2
        self.batch_size = 5