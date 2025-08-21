import re
from app.models import RFC5424SyslogMessage


class RFC5424Parser:
    """RFC 5424 Syslog message parser."""
    
    RFC5424_PATTERN = re.compile(
        r'^<(\d+)>'  # Priority
        r'(\d+)\s+'  # Version
        r'(\S+)\s+'  # Timestamp
        r'(\S+)\s+'  # Hostname
        r'(\S+)\s+'  # App-Name
        r'(\S+)\s+'  # ProcID
        r'(\S+)\s+'  # MsgID
        r'(\S+)\s*'  # Structured-Data
        r'(.*)$'     # Message
    )
    
    @staticmethod
    def parse_priority(priority: int) -> tuple:
        """Extract facility and severity from priority."""
        facility = priority >> 3
        severity = priority & 7
        return facility, severity
    
    def parse(self, raw_message: str) -> RFC5424SyslogMessage:
        """Parse RFC 5424 message."""
        match = self.RFC5424_PATTERN.match(raw_message.strip())
        
        if not match:
            raise ValueError("Invalid RFC 5424 syslog format")
        
        priority_str, version_str, timestamp_str, hostname, app_name, proc_id, msg_id, structured_data, message = match.groups()
        
        try:
            priority = int(priority_str)
            version = int(version_str)
            facility, severity = self.parse_priority(priority)
            
            # Handle nil values
            app_name = None if app_name == "-" else app_name
            proc_id = None if proc_id == "-" else proc_id
            msg_id = None if msg_id == "-" else msg_id
            structured_data = None if structured_data == "-" else structured_data
            
            return RFC5424SyslogMessage(
                priority=priority,
                facility=facility,
                severity=severity,
                version=version,
                timestamp=timestamp_str,
                hostname=hostname,
                app_name=app_name,
                proc_id=proc_id,
                msg_id=msg_id,
                structured_data=structured_data,
                message=message
            )
            
        except ValueError as e:
            raise ValueError(f"Parsing error: {e}")