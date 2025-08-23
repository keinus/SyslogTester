"""
RFC 3164/5424 Syslog 파서 애플리케이션의 설정 정보입니다.

이 모듈은 Pydantic의 BaseSettings를 사용하여 애플리케이션 설정을 정의하고,
기본값과 환경 변수 지원을 제공합니다.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 구성입니다.

    이 클래스는 모든 애플리케이션 설정을 기본값과 함께 정의합니다.
    설정은 환경 변수를 통해 재정의할 수 있습니다.
    """
    app_name: str = "RFC 3164/5424 Syslog 파서"
    version: str = "2.0.0"
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False

    class Config:
        """환경 변수를 .env 파일에서 로드하기 위한 구성 클래스입니다.
        """
        env_file = ".env"


settings = Settings()
