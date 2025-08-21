import datetime
import re
from app.models import SyslogMessage


class RFC3164Parser:
    """RFC 3164 Syslog message parser."""
    
    MONTHS = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    RFC3164_PATTERN = re.compile(
        r'^<(\d+)>'
        r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(\S+)\s+'
        r'([^:\[\s]+)(?:\[(\d+)\])?:\s*'
        r'(.*)$'
    )
    
    @staticmethod
    def parse_priority(priority: int) -> tuple:
        """Extract facility and severity from priority."""
        facility = priority >> 3
        severity = priority & 7
        return facility, severity
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> str:
        """Convert RFC 3164 timestamp to ISO format."""
        try:
            parts = timestamp_str.split()
            month_name = parts[0]
            day = int(parts[1])
            time_part = parts[2]
            
            month = RFC3164Parser.MONTHS.get(month_name)
            if not month:
                raise ValueError(f"Invalid month: {month_name}")
            
            year = datetime.datetime.now().year
            hour, minute, second = map(int, time_part.split(':'))
            
            dt = datetime.datetime(year, month, day, hour, minute, second)
            return dt.isoformat()
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid timestamp format: {e}")
    
    def parse(self, raw_message: str) -> SyslogMessage:
        """Parse RFC 3164 message."""
        match = self.RFC3164_PATTERN.match(raw_message.strip())
        
        if not match:
            raise ValueError("Invalid RFC 3164 syslog format")
        
        priority_str, timestamp_str, hostname, tag, pid_str, message = match.groups()
        
        try:
            priority = int(priority_str)
            facility, severity = self.parse_priority(priority)
            timestamp = self.parse_timestamp(timestamp_str)
            pid = int(pid_str) if pid_str else None
            
            return SyslogMessage(
                priority=priority,
                facility=facility,
                severity=severity,
                timestamp=timestamp,
                hostname=hostname,
                tag=tag,
                pid=pid,
                message=message
            )
            
        except ValueError as e:
            raise ValueError(f"Parsing error: {e}")