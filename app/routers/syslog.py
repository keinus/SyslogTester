from fastapi import APIRouter, Form
from app.models import (
    SyslogRequest,
    GenerateRequest,
    MessageComponents,
    SyslogResponse,
)
from app.parsers import RFC3164Parser, RFC5424Parser
from app.generators import RFC3164MessageGenerator, RFC5424MessageGenerator
from app.senders import SyslogSender

router = APIRouter(prefix="/api/syslog", tags=["syslog"])

# Initialize instances
rfc3164_parser = RFC3164Parser()
rfc5424_parser = RFC5424Parser()
rfc3164_generator = RFC3164MessageGenerator()
rfc5424_generator = RFC5424MessageGenerator()
sender = SyslogSender()


@router.post("/parse", response_model=SyslogResponse)
async def parse_syslog(request: SyslogRequest):
    """Parse and send syslog message."""
    print(f"Received request: {request}")
    
    try:
        # Select parser based on RFC version
        if request.rfc_version == "5424":
            parsed_message = rfc5424_parser.parse(request.raw_message)
        else:
            parsed_message = rfc3164_parser.parse(request.raw_message)
        print(f"Message parsed successfully: {parsed_message}")
        
        if request.protocol.lower() == "udp":
            await sender.send_udp(request.raw_message, request.target_server, request.target_port)
        elif request.protocol.lower() == "tcp":
            await sender.send_tcp(request.raw_message, request.target_server, request.target_port)
        else:
            raise ValueError("Protocol must be 'udp' or 'tcp'")
        
        response = SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            sent_to=f"{request.target_server}:{request.target_port} ({request.protocol.upper()})"
        )
        
        print(f"Response: {response}")
        return response
        
    except ValueError as e:
        print(f"Validation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        print(f"Transmission error: {e}")
        return SyslogResponse(
            success=False,
            error=f"Transmission error: {str(e)}"
        )


@router.post("/parse-only", response_model=SyslogResponse)
async def parse_only(raw_message: str = Form(...), rfc_version: str = Form("3164")):
    """Parse syslog message only (no transmission)."""
    print(f"Parse-only request: {raw_message}, RFC: {rfc_version}")
    
    try:
        # Select parser based on RFC version
        if rfc_version == "5424":
            parsed_message = rfc5424_parser.parse(raw_message)
        else:
            parsed_message = rfc3164_parser.parse(raw_message)
        print(f"Parse-only successful: {parsed_message}")
        
        return SyslogResponse(
            success=True,
            parsed_message=parsed_message
        )
        
    except ValueError as e:
        print(f"Parse-only error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )


@router.post("/generate", response_model=SyslogResponse)
async def generate_syslog(request: GenerateRequest):
    """Generate and send syslog message from components."""
    print(f"Generate request: {request}")
    
    try:
        # Select generator based on RFC version
        if request.components.rfc_version == "5424":
            generated_message = rfc5424_generator.generate(request.components)
        else:
            generated_message = rfc3164_generator.generate(request.components)
        
        print(f"Generated message: {generated_message}")
        
        # Send the generated message
        if request.protocol.lower() == "udp":
            await sender.send_udp(generated_message, request.target_server, request.target_port)
        elif request.protocol.lower() == "tcp":
            await sender.send_tcp(generated_message, request.target_server, request.target_port)
        else:
            raise ValueError("Protocol must be 'udp' or 'tcp'")
        
        # Parse the generated message to return structured data
        if request.components.rfc_version == "5424":
            parsed_message = rfc5424_parser.parse(generated_message)
        else:
            parsed_message = rfc3164_parser.parse(generated_message)
        
        response = SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            generated_message=generated_message,
            sent_to=f"{request.target_server}:{request.target_port} ({request.protocol.upper()})"
        )
        
        print(f"Response: {response}")
        return response
        
    except ValueError as e:
        print(f"Generation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        print(f"Transmission error: {e}")
        return SyslogResponse(
            success=False,
            error=f"Transmission error: {str(e)}"
        )


@router.post("/generate-only", response_model=SyslogResponse)
async def generate_only(components: MessageComponents):
    """Generate syslog message only (no transmission)."""
    print(f"Generate-only request: {components}")
    
    try:
        # Select generator based on RFC version
        if components.rfc_version == "5424":
            generated_message = rfc5424_generator.generate(components)
            parsed_message = rfc5424_parser.parse(generated_message)
        else:
            generated_message = rfc3164_generator.generate(components)
            parsed_message = rfc3164_parser.parse(generated_message)
        
        print(f"Generated message: {generated_message}")
        
        return SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            generated_message=generated_message
        )
        
    except ValueError as e:
        print(f"Generation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )


@router.get("/validate/{message}/{rfc_version}")
async def validate_format(message: str, rfc_version: str = "3164"):
    """Validate RFC format."""
    try:
        # Select parser based on RFC version
        if rfc_version == "5424":
            parsed = rfc5424_parser.parse(message)
        else:
            parsed = rfc3164_parser.parse(message)
        return {
            "valid": True,
            "parsed": parsed.model_dump(),
            "rfc_version": rfc_version
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "rfc_version": rfc_version
        }