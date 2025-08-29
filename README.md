# 📊 RFC 3164/5424 Syslog Parser & Generator

RFC 3164 및 5424 표준을 완벽 지원하는 현대적이고 포괄적인 시스로그 메시지 파싱, 생성, 전송 웹 애플리케이션입니다. FastAPI로 구축되었으며 아름답고 반응형 사용자 인터페이스를 제공합니다.

## ✨ 주요 기능

### 🏆 핵심 기능
- **RFC 표준 완벽 지원**: RFC 3164 및 RFC 5424 시스로그 메시지 파싱 및 생성
- **동적 메시지 컴포넌트**: 키-값 쌍으로 구성된 유연한 메시지 구성 시스템
- **랜덤 값 생성**: 테스트용 랜덤 IP, 포트, 타임스탬프 등 자동 생성
- **다중 전송 기능**: 설정 가능한 횟수만큼 반복 전송 (1~10,000회)
- **무제한 전송 모드**: 취소할 때까지 지속적으로 전송하는 모드
- **네트워크 전송**: UDP 및 TCP 프로토콜 지원
- **실시간 진행률**: 전송 성공/실패 카운트 실시간 표시

### 🎨 현대적인 UI
- **3열 레이아웃**: 예제, 설정, 결과 섹션으로 구성
- **접이식 인터페이스**: 각 섹션별 접기/펼치기 기능
- **반응형 디자인**: 데스크톱, 태블릿, 모바일 완벽 지원
- **실시간 피드백**: 실시간 상태 업데이트 및 오류 처리
- **예제 라이브러리**: 사용자 정의 예제 저장/관리 기능
- **키보드 단축키**: Ctrl+Enter, Ctrl+R로 효율적인 워크플로우

### ⚡ 기술적 특징
- **클린 아키텍처**: 관심사가 분리된 모듈식 FastAPI 구조
- **타입 안정성**: 완전한 Pydantic 모델 유효성 검사
- **포괄적 오류 처리**: 사용자 친화적 오류 메시지 및 피드백
- **API 문서화**: 자동 생성되는 OpenAPI/Swagger 문서
- **상태 모니터링**: 내장된 헬스 체크 엔드포인트
- **데이터베이스 관리**: SQLite 기반 예제 저장 및 관리

## 📦 포함된 예제

### 표준 Syslog 예제
- 시스템 인증 로그
- 프로세스 관리 메시지  
- 애플리케이션 알림

## 📁 프로젝트 구조

```
PacketTester/
├── app/                    # FastAPI 애플리케이션
│   ├── core/              # 설정 및 구성
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py    # 데이터베이스 관리
│   ├── models/            # Pydantic 데이터 모델
│   │   ├── __init__.py
│   │   ├── syslog.py
│   │   └── example.py     # 예제 모델
│   ├── parsers/           # RFC 메시지 파서
│   │   ├── __init__.py
│   │   ├── rfc3164.py
│   │   └── rfc5424.py
│   ├── generators/        # 메시지 생성기
│   │   ├── __init__.py
│   │   ├── rfc3164.py
│   │   └── rfc5424.py
│   ├── senders/           # 네트워크 전송
│   │   ├── __init__.py
│   │   └── syslog_sender.py
│   ├── routers/           # API 엔드포인트
│   │   ├── __init__.py
│   │   ├── info.py
│   │   ├── syslog.py
│   │   ├── test.py
│   │   └── examples.py    # 예제 관리 API
│   └── main.py            # FastAPI 앱 구성
├── static/                # 프론트엔드 자산
│   ├── css/
│   │   └── styles.css     # 현대적 반응형 스타일링
│   ├── js/
│   │   └── app.js         # 프론트엔드 JavaScript
│   └── index.html         # 메인 UI
├── run.py                 # 애플리케이션 진입점
├── pyproject.toml         # 프로젝트 설정 (uv)
├── requirements.txt       # Python 의존성
├── .gitignore            # Git 무시 파일
├── LICENSE               # MIT 라이선스
└── README.md             # 프로젝트 문서
```

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.10+
- pip 또는 uv 패키지 매니저

### 설치 방법

#### uv 사용 (권장)
```bash
# 저장소 복제
git clone https://github.com/username/PacketTester.git
cd PacketTester

# uv로 종속성 설치 및 실행
uv run python run.py
```

#### pip 사용
```bash
# 저장소 복제
git clone https://github.com/username/PacketTester.git
cd PacketTester

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 종속성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python run.py
```

### 애플리케이션 접속
- **웹 인터페이스**: http://localhost:8001
- **API 문서**: http://localhost:8001/docs
- **API 정보**: http://localhost:8001/api/

## 📖 사용 가이드

### 1. 메시지 컴포넌트 모드 (기본)
1. RFC 버전 선택 (3164 또는 5424)
2. 메시지 컴포넌트 입력:
   - **Priority**: 우선순위 (Facility*8 + Severity)
   - **Facility**: 0=kernel, 4=security, 16=local0
   - **Severity**: 0=emergency, 4=warning, 6=info
   - **Hostname**: 소스 시스템 식별자
   - **Tag/App Name**: 애플리케이션 식별자
3. 키-값 메시지 컴포넌트 추가 (랜덤 체크박스로 자동 생성 가능)
4. 대상 서버 구성 (IP, 포트, 프로토콜)
5. 전송 설정 (횟수, 딜레이, 무제한 모드)
6. "Generate & Send" 또는 "Generate Only" 클릭

### 2. 원시 메시지 모드
1. "Raw Message" 입력 모드로 전환
2. 파싱할 RFC 버전 선택
3. 완전한 시스로그 메시지 입력 또는 붙여넣기
4. "Parse & Send" 또는 "Parse Only" 클릭

### 3. 다중 전송 기능
1. **전송 횟수**: 1~10,000회 설정
2. **딜레이**: 전송 간 대기시간(ms) 설정
3. **무제한 모드**: 체크 시 취소할 때까지 지속 전송
4. 전송 중 "Cancel Transmission" 버튼으로 중단 가능
5. 실시간 진행률 및 성공/실패 카운트 확인

### 4. 예제 관리
1. **예제 적용**: 왼쪽 예제 클릭으로 메시지 구성에 자동 적용
2. **예제 저장**: 결과 섹션에서 생성된 메시지를 예제로 저장
3. **예제 삭제**: 각 예제 항목의 삭제 버튼(🗑️) 클릭

## 🔧 API 엔드포인트

### Syslog 작업
- `POST /api/syslog/generate` - 컴포넌트로부터 메시지 생성 및 전송
- `POST /api/syslog/generate-only` - 메시지 생성만 (전송 없음)
- `POST /api/syslog/parse` - 원시 메시지 파싱 및 전송
- `POST /api/syslog/parse-only` - 원시 메시지 파싱만
- `GET /api/syslog/validate/{message}/{rfc_version}` - 메시지 형식 유효성 검사

### 예제 관리
- `GET /api/examples/` - 모든 사용자 정의 예제 조회
- `POST /api/examples/` - 새 예제 생성
- `GET /api/examples/{example_id}` - 특정 예제 조회
- `PUT /api/examples/{example_id}` - 예제 수정
- `DELETE /api/examples/{example_id}` - 예제 삭제

### 테스트 및 정보
- `GET /api/` - API 정보 및 엔드포인트
- `GET /health` - 헬스 체크 엔드포인트

## 🔒 보안 고려사항

이 애플리케이션은 **테스트 및 개발 목적**으로 설계되었습니다. 프로덕션 사용 시:

- 인증 및 권한 부여 구현
- 속도 제한 및 입력 유효성 검사 추가
- 프로덕션 환경에서 HTTPS 사용
- 모든 사용자 입력 검증 및 정리
- 적절한 네트워크 보안 구성

## 📋 개발 가이드

### 로컬 개발 환경 설정
```bash
# 개발 모드로 실행 (자동 리로드)
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 또는 uv 사용
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 코드 스타일
- Python: PEP 8 준수
- JavaScript: ES6+ 모던 문법 사용
- CSS: BEM 방법론 권장

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 🔄 업데이트 히스토리

### v1.0.0 (2025-01-21)
- RFC 3164/5424 완전 지원
- 동적 메시지 컴포넌트 시스템
- 다중/무제한 전송 기능
- 사용자 정의 예제 관리
- 접이식 UI 및 랜덤 값 생성
- 포괄적 오류 처리 및 상태 관리
