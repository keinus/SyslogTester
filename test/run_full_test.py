#!/usr/bin/env python3
"""
완전한 Syslog 테스트 실행기
디버그 서버를 시작하고 모든 테스트를 실행한 후 결과를 표시합니다.
"""
import asyncio
import time
import threading
import signal
import sys
from test.debug_syslog_server import DebugSyslogServer
from test_syslog import SyslogTester


class FullTestRunner:
    """전체 테스트를 실행하는 클래스"""
    
    def __init__(self):
        self.server = DebugSyslogServer()
        self.tester = SyslogTester()
        self.running = True
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print("\n테스트 중단 요청을 받았습니다...")
        self.running = False
        self.server.stop()
        sys.exit(0)
    
    async def run_tests_with_server(self):
        """서버와 함께 테스트를 실행합니다."""
        print("="*60)
        print("  RFC 3164/5424 Syslog 완전한 테스트")
        print("="*60)
        print()
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # 디버그 서버 시작
            print("1. 디버그 Syslog 서버 시작 중...")
            self.server.start()
            
            # 서버가 시작될 시간을 줍니다
            await asyncio.sleep(2)
            
            print("2. 테스트 실행 중...")
            print()
            
            # 모든 테스트 실행
            await self.tester.run_all_tests()
            
            print()
            print("3. 서버에서 받은 메시지 확인 중...")
            await asyncio.sleep(1)
            
            # 서버에서 받은 메시지 확인
            received_messages = self.server.get_received_messages()
            
            if received_messages:
                print(f"\n서버가 받은 메시지 총 {len(received_messages)}개:")
                print("-" * 60)
                
                for i, msg in enumerate(received_messages, 1):
                    print(f"[{i}] {msg['timestamp']} - {msg['protocol']} from {msg['client']}")
                    print(f"    {msg['message'][:100]}{'...' if len(msg['message']) > 100 else ''}")
                    print()
                
                # 프로토콜별 통계
                udp_count = len([m for m in received_messages if m['protocol'] == 'UDP'])
                tcp_count = len([m for m in received_messages if m['protocol'] == 'TCP'])
                
                print(f"UDP 메시지: {udp_count}개")
                print(f"TCP 메시지: {tcp_count}개")
                
                if tcp_count > 0:
                    print("✅ TCP 전송 테스트도 성공!")
                else:
                    print("ℹ️ TCP 전송 테스트를 위해서는 서버가 미리 실행되어야 합니다.")
                
            else:
                print("서버가 받은 메시지가 없습니다.")
            
            print()
            print("4. 최종 결과 요약")
            print("-" * 60)
            
            # 테스트 결과 요약
            test_results = self.tester.test_results
            total = len(test_results)
            success = len([r for r in test_results if r["status"] == "SUCCESS"])
            
            print(f"총 테스트: {total}개")
            print(f"성공: {success}개")
            print(f"실패: {total - success}개")
            print(f"성공률: {(success/total)*100:.1f}%")
            
            if received_messages:
                print(f"전송 테스트: UDP {udp_count}개, TCP {tcp_count}개 메시지 수신됨")
            
            print()
            print("5. 파일 저장")
            print("-" * 60)
            print("✅ test_results.json - 테스트 결과")
            
            if received_messages:
                import json
                with open("received_messages.json", "w", encoding="utf-8") as f:
                    json.dump(received_messages, f, ensure_ascii=False, indent=2)
                print("✅ received_messages.json - 서버가 받은 메시지")
            
        except Exception as e:
            print(f"테스트 실행 중 오류 발생: {e}")
            
        finally:
            # 서버 정리
            print("\n서버 정리 중...")
            self.server.stop()
            await asyncio.sleep(1)
    
    def run_quick_test(self):
        """서버 없이 빠른 테스트만 실행합니다."""
        print("="*60)
        print("  RFC 3164/5424 Syslog 빠른 테스트 (서버 없음)")
        print("="*60)
        print()
        
        async def quick_test():
            # 생성 및 파싱 테스트만 실행
            rfc3164_cases = self.tester.create_rfc3164_test_cases()
            await self.tester.test_message_generation_and_parsing(rfc3164_cases, "3164")
            
            rfc5424_cases = self.tester.create_rfc5424_test_cases()
            await self.tester.test_message_generation_and_parsing(rfc5424_cases, "5424")
            
            self.tester.test_priority_calculation()
            self.tester.test_timestamp_formats()
            self.tester.generate_test_report()
        
        asyncio.run(quick_test())


def main():
    """메인 함수"""
    runner = FullTestRunner()
    
    print("Syslog 테스트 실행기")
    print("1. 전체 테스트 (서버 포함) - 서버를 시작하고 전송 테스트까지 수행")
    print("2. 빠른 테스트 (서버 없음) - 생성/파싱 테스트만 수행")
    print()
    
    choice = input("선택하세요 (1 또는 2, 기본값 1): ").strip() or "1"
    
    if choice == "2":
        runner.run_quick_test()
    else:
        print("\n전체 테스트를 시작합니다...")
        print("테스트 중단은 Ctrl+C를 누르세요.")
        print()
        
        asyncio.run(runner.run_tests_with_server())


if __name__ == "__main__":
    main()