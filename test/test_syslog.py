#!/usr/bin/env python3
"""
RFC 3164/5424 Syslog 테스트 코드
UI를 통해 다양한 syslog 메시지를 생성하고 검증하는 테스트 스크립트
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from app.models.syslog import MessageComponents
from app.parsers import parse_service
from app.generators import generator_service
from app.senders.syslog_sender import SyslogSender


class SyslogTester:
    """Syslog 메시지 생성 및 테스트를 위한 클래스"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.server = "127.0.0.1"
        self.port = 5140
    
    def print_header(self, title: str):
        """테스트 헤더를 출력합니다."""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_test_case(self, case_name: str):
        """테스트 케이스 헤더를 출력합니다."""
        print(f"\n--- {case_name} ---")
    
    def create_rfc3164_test_cases(self) -> List[MessageComponents]:
        """RFC 3164 테스트 케이스들을 생성합니다."""
        test_cases = []
        
        # 기본 RFC 3164 메시지
        test_cases.append(MessageComponents(
            rfc_version="3164",
            facility=16,  # local0
            severity=6,   # info
            hostname="test-server",
            tag="testapp",
            pid=1234,
            message="Basic RFC 3164 test message"
        ))
        
        # 높은 우선순위 메시지
        test_cases.append(MessageComponents(
            rfc_version="3164",
            facility=4,   # security
            severity=1,   # alert
            hostname="security-server",
            tag="auth",
            pid=5678,
            message="Security alert: Failed authentication attempt"
        ))
        
        # 시스템 메시지
        test_cases.append(MessageComponents(
            rfc_version="3164",
            facility=0,   # kernel
            severity=3,   # error
            hostname="kernel-server",
            tag="kernel",
            message="System error: Memory allocation failed"
        ))
        
        # 긴 메시지
        test_cases.append(MessageComponents(
            rfc_version="3164",
            facility=16,  # local0
            severity=6,   # info
            hostname="app-server",
            tag="longmsg",
            pid=9999,
            message="This is a very long message to test the RFC 3164 format handling of extended content. " +
                   "It contains multiple sentences and should be properly formatted according to the standard. " +
                   "This helps verify that our implementation can handle messages of various lengths correctly."
        ))
        
        return test_cases
    
    def create_rfc5424_test_cases(self) -> List[MessageComponents]:
        """RFC 5424 테스트 케이스들을 생성합니다."""
        test_cases = []
        
        # 기본 RFC 5424 메시지
        test_cases.append(MessageComponents(
            rfc_version="5424",
            facility=16,  # local0
            severity=6,   # info
            hostname="test-server",
            app_name="testapp",
            proc_id="1234",
            msg_id="MSG001",
            structured_data="[exampleSDID@32473 iut=\"3\" eventSource=\"Application\" eventID=\"1011\"]",
            message="Basic RFC 5424 test message"
        ))
        
        # 구조화된 데이터가 있는 메시지
        test_cases.append(MessageComponents(
            rfc_version="5424",
            facility=4,   # security
            severity=2,   # critical
            hostname="security-server",
            app_name="auth-service",
            proc_id="5678",
            msg_id="AUTH-FAIL",
            structured_data="[auth@32473 user=\"admin\" ip=\"192.168.1.100\" attempts=\"5\"]",
            message="Authentication failure detected"
        ))
        
        # 다중 구조화된 데이터
        test_cases.append(MessageComponents(
            rfc_version="5424",
            facility=16,  # local0
            severity=4,   # warning
            hostname="metrics-server",
            app_name="monitoring",
            proc_id="worker-01",
            msg_id="METRIC",
            structured_data="[metrics@32473 cpu=\"85.5\" memory=\"78.2\"][alert@32473 threshold=\"80\" status=\"warning\"]",
            message="System metrics threshold exceeded"
        ))
        
        # 구조화된 데이터 없는 메시지
        test_cases.append(MessageComponents(
            rfc_version="5424",
            facility=1,   # mail
            severity=6,   # info
            hostname="mail-server",
            app_name="postfix",
            proc_id="smtp[2345]",
            msg_id="DELIVERED",
            structured_data="-",
            message="Email delivered successfully to user@example.com"
        ))
        
        return test_cases
    
    async def test_message_generation_and_parsing(self, test_cases: List[MessageComponents], rfc_version: str):
        """메시지 생성 및 파싱 테스트를 수행합니다."""
        self.print_header(f"RFC {rfc_version} 메시지 생성 및 파싱 테스트")
        
        for i, components in enumerate(test_cases, 1):
            self.print_test_case(f"Test Case {i}")
            
            try:
                # 메시지 생성
                generated_message = generator_service.generate(rfc_version, components)
                print(f"생성된 메시지: {generated_message}")
                
                # 메시지 파싱
                parsed_message = parse_service.parse(rfc_version, generated_message)
                print(f"파싱 결과:")
                print(f"  - Priority: {parsed_message.priority}")
                print(f"  - Facility: {parsed_message.facility}")
                print(f"  - Severity: {parsed_message.severity}")
                print(f"  - Timestamp: {parsed_message.timestamp}")
                print(f"  - Hostname: {parsed_message.hostname}")
                
                if rfc_version == "3164" and hasattr(parsed_message, 'tag'):
                    print(f"  - Tag: {parsed_message.tag}")
                    if parsed_message.pid:
                        print(f"  - PID: {parsed_message.pid}")
                elif rfc_version == "5424":
                    if hasattr(parsed_message, 'app_name') and parsed_message.app_name:
                        print(f"  - App Name: {parsed_message.app_name}")
                    if hasattr(parsed_message, 'proc_id') and parsed_message.proc_id:
                        print(f"  - Proc ID: {parsed_message.proc_id}")
                    if hasattr(parsed_message, 'msg_id') and parsed_message.msg_id:
                        print(f"  - Msg ID: {parsed_message.msg_id}")
                    if hasattr(parsed_message, 'structured_data') and parsed_message.structured_data:
                        print(f"  - Structured Data: {parsed_message.structured_data}")
                
                print(f"  - Message: {parsed_message.message}")
                
                # 결과 저장
                self.test_results.append({
                    "test_case": f"RFC {rfc_version} Case {i}",
                    "status": "SUCCESS",
                    "generated_message": generated_message,
                    "parsed_data": parsed_message.model_dump()
                })
                
                print("✅ 테스트 성공")
                
            except Exception as e:
                print(f"❌ 테스트 실패: {str(e)}")
                self.test_results.append({
                    "test_case": f"RFC {rfc_version} Case {i}",
                    "status": "FAILED",
                    "error": str(e)
                })
    
    async def test_message_transmission(self, test_cases: List[MessageComponents], rfc_version: str):
        """메시지 전송 테스트를 수행합니다."""
        self.print_header(f"RFC {rfc_version} 메시지 전송 테스트")
        
        for i, components in enumerate(test_cases[:2], 1):  # 처음 2개 케이스만 전송 테스트
            self.print_test_case(f"Transmission Test {i}")
            
            try:
                # 메시지 생성
                generated_message = generator_service.generate(rfc_version, components)
                print(f"전송할 메시지: {generated_message}")
                
                # UDP로 전송 테스트
                print(f"UDP로 {self.server}:{self.port}에 전송 중...")
                await SyslogSender.send("udp", generated_message, self.server, self.port)
                print("✅ UDP 전송 성공")
                
                time.sleep(0.1)  # 짧은 지연
                
                # TCP로 전송 테스트
                print(f"TCP로 {self.server}:{self.port}에 전송 중...")
                await SyslogSender.send("tcp", generated_message, self.server, self.port)
                print("✅ TCP 전송 성공")
                
                # 결과 저장
                self.test_results.append({
                    "test_case": f"RFC {rfc_version} Transmission {i}",
                    "status": "SUCCESS",
                    "message": generated_message,
                    "target": f"{self.server}:{self.port}"
                })
                
            except Exception as e:
                print(f"❌ 전송 실패: {str(e)}")
                self.test_results.append({
                    "test_case": f"RFC {rfc_version} Transmission {i}",
                    "status": "FAILED",
                    "error": str(e)
                })
    
    def test_priority_calculation(self):
        """우선순위 계산 테스트를 수행합니다."""
        self.print_header("우선순위 계산 테스트")
        
        test_cases = [
            {"facility": 0, "severity": 0, "expected_priority": 0},
            {"facility": 16, "severity": 6, "expected_priority": 134},
            {"facility": 4, "severity": 1, "expected_priority": 33},
            {"facility": 23, "severity": 7, "expected_priority": 191},
        ]
        
        for i, case in enumerate(test_cases, 1):
            self.print_test_case(f"Priority Test {i}")
            
            components = MessageComponents(
                rfc_version="3164",
                facility=case["facility"],
                severity=case["severity"],
                hostname="test-server",
                tag="priority-test",
                message="Priority calculation test"
            )
            
            try:
                generated_message = generator_service.generate("3164", components)
                parsed_message = parse_service.parse("3164", generated_message)
                
                expected = case["expected_priority"]
                actual = parsed_message.priority
                
                print(f"Facility: {case['facility']}, Severity: {case['severity']}")
                print(f"예상 우선순위: {expected}, 실제 우선순위: {actual}")
                
                if actual == expected:
                    print("✅ 우선순위 계산 정확")
                    status = "SUCCESS"
                else:
                    print("❌ 우선순위 계산 오류")
                    status = "FAILED"
                
                self.test_results.append({
                    "test_case": f"Priority Calculation {i}",
                    "status": status,
                    "expected": expected,
                    "actual": actual
                })
                
            except Exception as e:
                print(f"❌ 테스트 실패: {str(e)}")
                self.test_results.append({
                    "test_case": f"Priority Calculation {i}",
                    "status": "FAILED",
                    "error": str(e)
                })
    
    def test_timestamp_formats(self):
        """타임스탬프 형식 테스트를 수행합니다."""
        self.print_header("타임스탬프 형식 테스트")
        
        # RFC 3164 타임스탬프 테스트
        self.print_test_case("RFC 3164 Timestamp")
        
        components_3164 = MessageComponents(
            rfc_version="3164",
            facility=16,
            severity=6,
            hostname="timestamp-test",
            tag="ts-test",
            message="Timestamp format test"
        )
        
        try:
            generated_message = generator_service.generate("3164", components_3164)
            print(f"RFC 3164 메시지: {generated_message}")
            
            # 타임스탬프 패턴 확인 (예: Oct 11 22:14:15)
            import re
            rfc3164_pattern = r'<\d+>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}'
            if re.match(rfc3164_pattern, generated_message):
                print("✅ RFC 3164 타임스탬프 형식 올바름")
                status = "SUCCESS"
            else:
                print("❌ RFC 3164 타임스탬프 형식 오류")
                status = "FAILED"
            
            self.test_results.append({
                "test_case": "RFC 3164 Timestamp Format",
                "status": status,
                "message": generated_message
            })
            
        except Exception as e:
            print(f"❌ RFC 3164 타임스탬프 테스트 실패: {str(e)}")
        
        # RFC 5424 타임스탬프 테스트
        self.print_test_case("RFC 5424 Timestamp")
        
        components_5424 = MessageComponents(
            rfc_version="5424",
            facility=16,
            severity=6,
            hostname="timestamp-test",
            app_name="ts-test",
            message="Timestamp format test"
        )
        
        try:
            generated_message = generator_service.generate("5424", components_5424)
            print(f"RFC 5424 메시지: {generated_message}")
            
            # 타임스탬프 패턴 확인 (예: 2003-10-11T22:14:15.003Z)
            rfc5424_pattern = r'<\d+>1 \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z'
            if re.search(rfc5424_pattern, generated_message):
                print("✅ RFC 5424 타임스탬프 형식 올바름")
                status = "SUCCESS"
            else:
                print("❌ RFC 5424 타임스탬프 형식 오류")
                status = "FAILED"
            
            self.test_results.append({
                "test_case": "RFC 5424 Timestamp Format",
                "status": status,
                "message": generated_message
            })
            
        except Exception as e:
            print(f"❌ RFC 5424 타임스탬프 테스트 실패: {str(e)}")
    
    def generate_test_report(self):
        """테스트 결과 리포트를 생성합니다."""
        self.print_header("테스트 결과 리포트")
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] == "SUCCESS"])
        failed_tests = total_tests - successful_tests
        
        print(f"총 테스트 수: {total_tests}")
        print(f"성공한 테스트: {successful_tests}")
        print(f"실패한 테스트: {failed_tests}")
        print(f"성공률: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n실패한 테스트 목록:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"  - {result['test_case']}: {result.get('error', 'Unknown error')}")
        
        # JSON 형태로 결과 저장
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n상세 테스트 결과가 'test_results.json' 파일에 저장되었습니다.")
    
    async def run_all_tests(self):
        """모든 테스트를 실행합니다."""
        print("RFC 3164/5424 Syslog 테스트 시작")
        print(f"테스트 서버: {self.server}:{self.port}")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # RFC 3164 테스트
        rfc3164_cases = self.create_rfc3164_test_cases()
        await self.test_message_generation_and_parsing(rfc3164_cases, "3164")
        await self.test_message_transmission(rfc3164_cases, "3164")
        
        # RFC 5424 테스트
        rfc5424_cases = self.create_rfc5424_test_cases()
        await self.test_message_generation_and_parsing(rfc5424_cases, "5424")
        await self.test_message_transmission(rfc5424_cases, "5424")
        
        # 추가 테스트
        self.test_priority_calculation()
        self.test_timestamp_formats()
        
        # 결과 리포트 생성
        self.generate_test_report()


async def main():
    """메인 함수"""
    tester = SyslogTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())