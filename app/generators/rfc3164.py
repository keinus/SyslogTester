import datetime
from app.models import MessageComponents


class RFC3164MessageGenerator:
    """RFC 3164 Syslog message generator."""
    
    @staticmethod
    def generate_priority(facility: int, severity: int) -> int:
        """Generate priority from facility and severity."""
        return (facility << 3) + severity
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate RFC 3164 timestamp."""
        now = datetime.datetime.now()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f"{months[now.month-1]} {now.day:2d} {now.strftime('%H:%M:%S')}"
    
    def generate(self, components: MessageComponents) -> str:
        """Generate RFC 3164 message from components."""
        priority = components.priority
        if priority is None and components.facility is not None and components.severity is not None:
            priority = self.generate_priority(components.facility, components.severity)
        
        if priority is None:
            priority = 34  # Default: facility 4, severity 2
        
        timestamp = components.timestamp if components.timestamp else self.generate_timestamp()
        hostname = components.hostname or "localhost"
        tag = components.tag or "app"
        pid_str = f"[{components.pid}]" if components.pid else ""
        message = components.message or ""
        
        return f"<{priority}>{timestamp} {hostname} {tag}{pid_str}: {message}"