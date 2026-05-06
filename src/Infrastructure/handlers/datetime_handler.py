from datetime import datetime, timezone, timedelta

class DateTimeHandler:
    BRAZIL_TZ = timezone(timedelta(hours=-3))  # Brazil GMT-3
    
    @staticmethod
    def now() -> datetime:
        """Get current time in Brazil (GMT-3)"""
        return datetime.now(DateTimeHandler.BRAZIL_TZ)
    
    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC time"""
        return datetime.now(timezone.utc)