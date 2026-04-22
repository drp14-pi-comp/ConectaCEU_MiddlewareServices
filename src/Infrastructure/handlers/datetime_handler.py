from datetime import datetime
from zoneinfo import ZoneInfo

class DateTimeHandler:
    @staticmethod
    def now() -> datetime:
        """Get current time in Brazil (America/Sao_Paulo) with DST support"""
        return datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC time"""
        return datetime.now(ZoneInfo("UTC"))