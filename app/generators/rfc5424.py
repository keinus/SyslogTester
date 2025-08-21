import datetime
from app.models import MessageComponents


class RFC5424MessageGenerator:
    """RFC 5424 Syslog message generator."""
    
    @staticmethod
    def generate_priority(facility: int, severity: int) -> int:
        """Generate priority from facility and severity."""
        return (facility << 3) + severity
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate RFC 5424 timestamp (ISO 8601)."""
        return datetime.datetime.now().isoformat() + "Z"
    
    def generate(self, components: MessageComponents) -> str:
        """Generate RFC 5424 message from components."""
        priority = components.priority
        if priority is None and components.facility is not None and components.severity is not None:
            priority = self.generate_priority(components.facility, components.severity)
        
        if priority is None:
            priority = 34  # Default: facility 4, severity 2
        
        version = 1
        timestamp = components.timestamp if components.timestamp else self.generate_timestamp()
        hostname = components.hostname or "localhost"
        app_name = components.app_name or "-"
        proc_id = components.proc_id or "-"
        msg_id = components.msg_id or "-"
        structured_data = components.structured_data or "-"
        message = components.message or ""
        
        return f"<{priority}>{version} {timestamp} {hostname} {app_name} {proc_id} {msg_id} {structured_data} {message}"