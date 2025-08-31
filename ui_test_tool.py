#!/usr/bin/env python3
"""
UI 기반 Syslog 테스트 도구
간단한 명령줄 인터페이스로 syslog 메시지 생성 및 테스트
"""
import asyncio
import json
from typing import Optional
from datetime import datetime

from app.models.syslog import MessageComponents
from app.parsers import parse_service
from app.generators import generator_service
from app.senders.syslog_sender import SyslogSender


class UITestTool:
    """UI 기반 테스트 도구 클래스"""
    
    def __init__(self):
        self.test_history = []
    
    def print_header(self, title: str):
        """헤더를 출력합니다."""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_menu(self):
        """메뉴를 출력합니다."""
        print("\n메뉴:")
        print("1. RFC 3164 메시지 생성 및 테스트")
        print("2. RFC 5424 메시지 생성 및 테스트")
        print("3. Raw 메시지 파싱 테스트")
        print("4. 사전 정의된 테스트 케이스 실행")
        print("5. 테스트 히스토리 보기")
        print("6. 결과 파일로 저장")
        print("0. 종료")
        print()
    
    def get_user_input(self, prompt: str, default: str = "", required: bool = True) -> str:
        """사용자 입력을 받습니다."""
        if default:
            full_prompt = f"{prompt} (기본값: {default}): "
        else:
            full_prompt = f"{prompt}: "
        
        value = input(full_prompt).strip()
        
        if not value and default:
            return default
        elif not value and required:
            print("필수 입력 항목입니다.")
            return self.get_user_input(prompt, default, required)
        
        return value
    
    def get_int_input(self, prompt: str, min_val: int = 0, max_val: int = 999999, default: Optional[int] = None) -> Optional[int]:
        """정수 입력을 받습니다."""
        default_str = str(default) if default is not None else ""
        value_str = self.get_user_input(prompt, default_str, required=default is None)
        
        if not value_str and default is not None:
            return default
        
        try:
            value = int(value_str)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"값은 {min_val}에서 {max_val} 사이여야 합니다.")
                return self.get_int_input(prompt, min_val, max_val, default)
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
            return self.get_int_input(prompt, min_val, max_val, default)
    
    def create_rfc3164_message(self) -> MessageComponents:
        """RFC 3164 메시지 구성 요소를 입력받습니다."""
        self.print_header("RFC 3164 메시지 생성")
        
        print("RFC 3164 메시지 구성 요소를 입력하세요:")
        
        facility = self.get_int_input("Facility (0-23)", 0, 23, 16)
        severity = self.get_int_input("Severity (0-7)", 0, 7, 6)
        hostname = self.get_user_input("Hostname", "test-server")
        tag = self.get_user_input("Tag", "testapp")
        pid = self.get_int_input("Process ID (선택사항, Enter로 건너뛰기)", 0, 999999, None)
        message = self.get_user_input("Message", "Test message from UI tool")
        
        return MessageComponents(
            rfc_version="3164",
            facility=facility,
            severity=severity,
            hostname=hostname,
            tag=tag,
            pid=pid,
            message=message
        )
    
    def create_rfc5424_message(self) -> MessageComponents:
        """RFC 5424 메시지 구성 요소를 입력받습니다."""
        self.print_header("RFC 5424 메시지 생성")
        
        print("RFC 5424 메시지 구성 요소를 입력하세요:")
        
        facility = self.get_int_input("Facility (0-23)", 0, 23, 16)
        severity = self.get_int_input("Severity (0-7)", 0, 7, 6)
        hostname = self.get_user_input("Hostname", "test-server")
        app_name = self.get_user_input("Application Name", "testapp")
        proc_id = self.get_user_input("Process ID (선택사항)", "", required=False)
        msg_id = self.get_user_input("Message ID (선택사항)", "", required=False)
        
        print("\n구조화된 데이터 입력 (선택사항):")
        print("예: [exampleSDID@32473 iut=\"3\" eventSource=\"Application\"]")
        structured_data = self.get_user_input("Structured Data", "", required=False)
        
        message = self.get_user_input("Message", "Test message from UI tool")
        
        return MessageComponents(
            rfc_version="5424",
            facility=facility,
            severity=severity,
            hostname=hostname,
            app_name=app_name if app_name else None,
            proc_id=proc_id if proc_id else None,
            msg_id=msg_id if msg_id else None,
            structured_data=structured_data if structured_data else None,
            message=message
        )
    
    async def test_message_generation(self, components: MessageComponents):
        """메시지 생성 및 테스트를 수행합니다."""
        print(f"\n--- RFC {components.rfc_version} 메시지 생성 및 테스트 ---")
        
        try:
            # 메시지 생성
            print("1. 메시지 생성 중...")
            generated_message = generator_service.generate(components.rfc_version, components)
            print(f"생성된 메시지: {generated_message}")
            
            # 메시지 파싱
            print("\n2. 메시지 파싱 중...")
            parsed_message = parse_service.parse(components.rfc_version, generated_message)
            print("파싱 결과:")
            print(f"  - Priority: {parsed_message.priority}")
            print(f"  - Facility: {parsed_message.facility}")
            print(f"  - Severity: {parsed_message.severity}")
            print(f"  - Timestamp: {parsed_message.timestamp}")
            print(f"  - Hostname: {parsed_message.hostname}")
            
            if components.rfc_version == "3164" and hasattr(parsed_message, 'tag'):
                print(f"  - Tag: {parsed_message.tag}")
                if parsed_message.pid:
                    print(f"  - PID: {parsed_message.pid}")
            elif components.rfc_version == "5424":
                if hasattr(parsed_message, 'app_name') and parsed_message.app_name:
                    print(f"  - App Name: {parsed_message.app_name}")
                if hasattr(parsed_message, 'proc_id') and parsed_message.proc_id:
                    print(f"  - Proc ID: {parsed_message.proc_id}")
                if hasattr(parsed_message, 'msg_id') and parsed_message.msg_id:
                    print(f"  - Msg ID: {parsed_message.msg_id}")
                if hasattr(parsed_message, 'structured_data') and parsed_message.structured_data:
                    print(f"  - Structured Data: {parsed_message.structured_data}")
            
            print(f"  - Message: {parsed_message.message}")
            
            # 전송 테스트 여부 묻기
            send_test = input("\n3. 전송 테스트를 수행하시겠습니까? (y/N): ").strip().lower()
            
            if send_test == 'y':
                await self.test_message_transmission(generated_message)
            
            # 히스토리에 저장
            test_record = {
                "timestamp": datetime.now().isoformat(),
                "rfc_version": components.rfc_version,
                "generated_message": generated_message,
                "parsed_data": parsed_message.model_dump(),
                "status": "SUCCESS"
            }
            self.test_history.append(test_record)
            
            print("✅ 테스트 완료!")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            
            # 실패도 히스토리에 저장
            test_record = {
                "timestamp": datetime.now().isoformat(),
                "rfc_version": components.rfc_version,
                "status": "FAILED",
                "error": str(e)
            }
            self.test_history.append(test_record)
    
    async def test_message_transmission(self, message: str):
        """메시지 전송 테스트를 수행합니다."""
        print("\n전송 설정:")
        server = self.get_user_input("서버 주소", "127.0.0.1")
        port = self.get_int_input("포트 번호", 1, 65535, 5140)
        
        protocol_choice = input("프로토콜 (1: UDP, 2: TCP, 3: 둘 다, 기본값: 1): ").strip() or "1"
        
        protocols = []
        if protocol_choice in ["1", "3"]:
            protocols.append("udp")
        if protocol_choice in ["2", "3"]:
            protocols.append("tcp")
        
        for protocol in protocols:
            try:
                print(f"\n{protocol.upper()}로 {server}:{port}에 전송 중...")
                await SyslogSender.send(protocol, message, server, port)
                print(f"✅ {protocol.upper()} 전송 성공")
            except Exception as e:
                print(f"❌ {protocol.upper()} 전송 실패: {str(e)}")
    
    def test_raw_message_parsing(self):
        """Raw 메시지 파싱 테스트를 수행합니다."""
        self.print_header("Raw 메시지 파싱 테스트")
        
        print("파싱할 raw syslog 메시지를 입력하세요:")
        print("예제:")
        print("  RFC 3164: <134>Oct 11 22:14:15 test-server testapp[1234]: Test message")
        print("  RFC 5424: <134>1 2003-10-11T22:14:15.003Z test-server testapp 1234 MSG001 - Test message")
        print()
        
        raw_message = input("Raw Message: ").strip()
        if not raw_message:
            print("메시지가 입력되지 않았습니다.")
            return
        
        rfc_version = input("RFC 버전 (3164/5424, 기본값: 3164): ").strip() or "3164"
        
        try:
            print(f"\nRFC {rfc_version}로 파싱 중...")
            parsed_message = parse_service.parse(rfc_version, raw_message)
            
            print("파싱 결과:")
            print(json.dumps(parsed_message.model_dump(), indent=2, ensure_ascii=False))
            
            # 히스토리에 저장
            test_record = {
                "timestamp": datetime.now().isoformat(),
                "test_type": "raw_parsing",
                "rfc_version": rfc_version,
                "raw_message": raw_message,
                "parsed_data": parsed_message.model_dump(),
                "status": "SUCCESS"
            }
            self.test_history.append(test_record)
            
            print("✅ 파싱 성공!")
            
        except Exception as e:
            print(f"❌ 파싱 실패: {str(e)}")
            
            test_record = {
                "timestamp": datetime.now().isoformat(),
                "test_type": "raw_parsing",
                "rfc_version": rfc_version,
                "raw_message": raw_message,
                "status": "FAILED",
                "error": str(e)
            }
            self.test_history.append(test_record)
    
    def run_predefined_tests(self):
        """사전 정의된 테스트 케이스들을 실행합니다."""
        self.print_header("사전 정의된 테스트 케이스 실행")
        
        # 간단한 테스트 케이스들
        test_cases = [
            # RFC 3164 케이스들
            MessageComponents(
                rfc_version="3164",
                facility=16, severity=6,
                hostname="web-server", tag="nginx", pid=1234,
                message="HTTP request processed"
            ),
            MessageComponents(
                rfc_version="3164",
                facility=4, severity=2,
                hostname="auth-server", tag="sshd", pid=5678,
                message="Authentication failure for user root"
            ),
            
            # RFC 5424 케이스들
            MessageComponents(
                rfc_version="5424",
                facility=16, severity=6,
                hostname="api-server", app_name="api-gateway", 
                proc_id="worker-1", msg_id="REQ001",
                structured_data='[request@32473 method="GET" path="/api/users" status="200"]',
                message="API request completed successfully"
            ),
            MessageComponents(
                rfc_version="5424",
                facility=1, severity=4,
                hostname="mail-server", app_name="postfix",
                proc_id="smtp[2345]", msg_id="BOUNCE",
                structured_data='-',
                message="Mail delivery failed: user not found"
            ),
        ]
        
        print(f"{len(test_cases)}개의 사전 정의된 테스트 케이스를 실행합니다...\n")
        
        async def run_tests():
            for i, components in enumerate(test_cases, 1):
                print(f"--- 테스트 케이스 {i} (RFC {components.rfc_version}) ---")
                await self.test_message_generation(components)
                print()
        
        asyncio.run(run_tests())
    
    def show_test_history(self):
        """테스트 히스토리를 보여줍니다."""
        self.print_header("테스트 히스토리")
        
        if not self.test_history:
            print("테스트 히스토리가 없습니다.")
            return
        
        print(f"총 {len(self.test_history)}개의 테스트가 실행되었습니다.\n")
        
        for i, record in enumerate(self.test_history, 1):
            timestamp = record.get("timestamp", "Unknown")
            status = record.get("status", "Unknown")
            rfc_version = record.get("rfc_version", "Unknown")
            
            status_icon = "✅" if status == "SUCCESS" else "❌"
            
            print(f"[{i}] {timestamp} - RFC {rfc_version} - {status_icon} {status}")
            
            if "generated_message" in record:
                msg = record["generated_message"]
                print(f"    메시지: {msg[:60]}{'...' if len(msg) > 60 else ''}")
            elif "raw_message" in record:
                msg = record["raw_message"]
                print(f"    Raw: {msg[:60]}{'...' if len(msg) > 60 else ''}")
            
            if status == "FAILED" and "error" in record:
                print(f"    오류: {record['error']}")
            
            print()
    
    def save_results_to_file(self):
        """결과를 파일로 저장합니다."""
        if not self.test_history:
            print("저장할 테스트 결과가 없습니다.")
            return
        
        filename = input("저장할 파일명 (기본값: ui_test_results.json): ").strip() or "ui_test_results.json"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.test_history, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 테스트 결과가 '{filename}' 파일에 저장되었습니다.")
            print(f"총 {len(self.test_history)}개의 테스트 결과가 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {str(e)}")
    
    async def run(self):
        """메인 실행 함수"""
        self.print_header("RFC 3164/5424 Syslog UI 테스트 도구")
        
        print("이 도구를 사용하여 syslog 메시지를 생성하고 테스트할 수 있습니다.")
        print("각 기능을 선택하여 대화형으로 syslog 메시지를 만들어보세요.")
        
        while True:
            self.print_menu()
            choice = input("선택하세요 (0-6): ").strip()
            
            if choice == "0":
                print("테스트 도구를 종료합니다.")
                if self.test_history:
                    save = input("종료하기 전에 테스트 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save == 'y':
                        self.save_results_to_file()
                break
                
            elif choice == "1":
                components = self.create_rfc3164_message()
                await self.test_message_generation(components)
                
            elif choice == "2":
                components = self.create_rfc5424_message()
                await self.test_message_generation(components)
                
            elif choice == "3":
                self.test_raw_message_parsing()
                
            elif choice == "4":
                self.run_predefined_tests()
                
            elif choice == "5":
                self.show_test_history()
                
            elif choice == "6":
                self.save_results_to_file()
                
            else:
                print("올바른 선택지를 입력해주세요.")
            
            input("\nEnter를 눌러 계속하세요...")


def main():
    """메인 함수"""
    tool = UITestTool()
    asyncio.run(tool.run())


if __name__ == "__main__":
    main()