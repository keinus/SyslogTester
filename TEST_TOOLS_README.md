# Syslog 테스트 도구 사용 가이드

이 프로젝트에는 RFC 3164 및 RFC 5424 syslog 메시지를 생성하고 테스트하기 위한 다양한 테스트 도구가 포함되어 있습니다.

## 테스트 도구 목록

### 1. 자동화된 테스트 스크립트 (`test_syslog.py`)
포괄적인 자동 테스트를 수행하는 스크립트입니다.

**특징:**
- RFC 3164 및 5424 메시지 생성 및 파싱 테스트
- 우선순위 계산 검증
- 타임스탬프 형식 검증
- UDP/TCP 전송 테스트
- 자동 테스트 리포트 생성

**실행방법:**
```bash
python3 test_syslog.py
```

**출력:**
- 콘솔에 실시간 테스트 결과 표시
- `test_results.json`: 상세 테스트 결과 저장

### 2. 디버그 Syslog 서버 (`debug_syslog_server.py`)
테스트용 syslog 메시지를 수신하는 디버그 서버입니다.

**특징:**
- UDP 및 TCP 프로토콜 지원
- 실시간 메시지 수신 및 표시
- 메시지 히스토리 관리
- 통계 정보 제공

**실행방법:**
```bash
python3 debug_syslog_server.py
```

**기본설정:**
- 서버 주소: 127.0.0.1
- 포트: 5140
- Ctrl+C로 종료

### 3. 통합 테스트 실행기 (`run_full_test.py`)
디버그 서버와 함께 전체 테스트를 실행합니다.

**특징:**
- 자동으로 디버그 서버 시작
- 모든 테스트 케이스 실행
- 전송된 메시지 수신 확인
- 종합 결과 리포트

**실행방법:**
```bash
python3 run_full_test.py
```

**옵션:**
1. 전체 테스트 (서버 포함): 모든 테스트 + 전송 테스트
2. 빠른 테스트 (서버 없음): 생성/파싱 테스트만

### 4. UI 테스트 도구 (`ui_test_tool.py`)
대화형 명령줄 인터페이스로 개별 테스트를 수행합니다.

**특징:**
- 대화형 메시지 생성
- 사용자 정의 테스트 케이스
- Raw 메시지 파싱 테스트
- 사전 정의된 테스트 케이스
- 테스트 히스토리 관리

**실행방법:**
```bash
python3 ui_test_tool.py
```

**메뉴 옵션:**
1. RFC 3164 메시지 생성 및 테스트
2. RFC 5424 메시지 생성 및 테스트
3. Raw 메시지 파싱 테스트
4. 사전 정의된 테스트 케이스 실행
5. 테스트 히스토리 보기
6. 결과 파일로 저장

## 테스트 시나리오

### 기본 테스트 시나리오
```bash
# 1. 빠른 검증
python3 test_syslog.py

# 2. 전송 테스트 포함
python3 run_full_test.py

# 3. 개별 메시지 테스트
python3 ui_test_tool.py
```

### 디버깅 시나리오
```bash
# 터미널 1: 디버그 서버 시작
python3 debug_syslog_server.py

# 터미널 2: 메시지 전송 테스트
python3 ui_test_tool.py
# 또는
python3 test_syslog.py
```

## 테스트 결과 파일

### `test_results.json`
자동화된 테스트의 상세 결과
```json
{
  "test_case": "RFC 3164 Case 1",
  "status": "SUCCESS",
  "generated_message": "<134>Aug 31 21:30:39 test-server testapp[1234]: Basic RFC 3164 test message",
  "parsed_data": {
    "priority": 134,
    "facility": 16,
    "severity": 6,
    ...
  }
}
```

### `received_messages.json`
디버그 서버가 수신한 메시지들
```json
{
  "timestamp": "2025-08-31 21:30:39.123",
  "protocol": "UDP",
  "client": "127.0.0.1:12345",
  "message": "<134>Aug 31 21:30:39 test-server testapp[1234]: Test message"
}
```

### `ui_test_results.json`
UI 도구의 테스트 결과

## 테스트 케이스 예시

### RFC 3164 테스트 케이스
```python
MessageComponents(
    rfc_version="3164",
    facility=16,  # local0
    severity=6,   # info
    hostname="test-server",
    tag="testapp",
    pid=1234,
    message="Basic RFC 3164 test message"
)
```

**생성된 메시지:**
```
<134>Aug 31 21:30:39 test-server testapp[1234]: Basic RFC 3164 test message
```

### RFC 5424 테스트 케이스
```python
MessageComponents(
    rfc_version="5424",
    facility=16,  # local0
    severity=6,   # info
    hostname="test-server",
    app_name="testapp",
    proc_id="1234",
    msg_id="MSG001",
    structured_data='[exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"]',
    message="Basic RFC 5424 test message"
)
```

**생성된 메시지:**
```
<134>1 2025-08-31T21:30:39.674326Z test-server testapp 1234 MSG001 [exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"] Basic RFC 5424 test message
```

## 우선순위 계산

Priority = Facility × 8 + Severity

**Facility 코드:**
- 0: kernel messages
- 1: mail system
- 4: security/authorization messages
- 16: local use facility (local0)
- 23: local use facility (local7)

**Severity 레벨:**
- 0: Emergency
- 1: Alert
- 2: Critical
- 3: Error
- 4: Warning
- 5: Notice
- 6: Informational
- 7: Debug

## 주요 수정사항

### RFC 5424 파서 개선
- 구조화된 데이터 정규식 개선
- 다중 구조화된 데이터 요소 지원
- nil 값 처리 개선

### 테스트 커버리지 확장
- 77.8% 성공률 달성 (18개 중 14개 성공)
- 타임스탬프 형식 검증 추가
- 우선순위 계산 검증 추가
- 긴 메시지 처리 테스트 추가

### 전송 테스트
- UDP 전송: 정상 작동
- TCP 전송: 서버 필요 (Connection refused는 정상적인 동작)

## 문제 해결

### TCP Connection Refused
TCP 전송 테스트에서 "Connection refused" 오류는 정상입니다. 이는 포트 5140에서 TCP 서버가 실행되지 않았기 때문입니다.

**해결방법:**
```bash
# 디버그 서버를 먼저 실행
python3 debug_syslog_server.py
```

### 파싱 오류
잘못된 형식의 메시지나 지원하지 않는 형식의 경우 파싱 오류가 발생할 수 있습니다.

**해결방법:**
- RFC 3164/5424 표준에 맞는 형식 확인
- UI 도구의 예시 참조
- 기본 테스트 케이스로 검증

## 활용 방법

1. **개발 중 테스트**: `ui_test_tool.py`로 개별 메시지 검증
2. **회귀 테스트**: `test_syslog.py`로 자동화된 테스트
3. **통합 테스트**: `run_full_test.py`로 전체 시스템 검증
4. **디버깅**: `debug_syslog_server.py`로 메시지 수신 확인