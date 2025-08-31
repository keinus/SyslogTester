#!/usr/bin/env python3
"""
디버깅용 간단한 Syslog 서버
UDP와 TCP 모두 지원하여 테스트 메시지를 받아 출력
"""
import asyncio
import socket
import threading
import time
from datetime import datetime


class DebugSyslogServer:
    """디버깅용 Syslog 서버 클래스"""
    
    def __init__(self, host="127.0.0.1", port=5140):
        self.host = host
        self.port = port
        self.running = False
        self.received_messages = []
        self.udp_server = None
        self.tcp_server = None
    
    def log_message(self, message: str, protocol: str, client: str):
        """받은 메시지를 로깅합니다."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'protocol': protocol,
            'client': client,
            'message': message
        }
        self.received_messages.append(log_entry)
        
        print(f"[{timestamp}] {protocol} from {client}:")
        print(f"  -> {message}")
        print()
    
    def handle_udp_message(self, data: bytes, addr):
        """UDP 메시지를 처리합니다."""
        try:
            message = data.decode('utf-8', errors='replace').strip()
            self.log_message(message, 'UDP', f"{addr[0]}:{addr[1]}")
        except Exception as e:
            print(f"UDP message decode error: {e}")
    
    def handle_tcp_client(self, client_socket, addr):
        """TCP 클라이언트를 처리합니다."""
        try:
            with client_socket:
                data = client_socket.recv(1024)
                if data:
                    message = data.decode('utf-8', errors='replace').strip()
                    self.log_message(message, 'TCP', f"{addr[0]}:{addr[1]}")
        except Exception as e:
            print(f"TCP client handler error: {e}")
    
    def start_udp_server(self):
        """UDP 서버를 시작합니다."""
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind((self.host, self.port))
            udp_socket.settimeout(1.0)  # 1초 타임아웃
            
            print(f"UDP 서버가 {self.host}:{self.port}에서 시작되었습니다.")
            
            while self.running:
                try:
                    data, addr = udp_socket.recvfrom(1024)
                    self.handle_udp_message(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"UDP server error: {e}")
                    break
            
            udp_socket.close()
            print("UDP 서버가 종료되었습니다.")
            
        except Exception as e:
            print(f"UDP 서버 시작 실패: {e}")
    
    def start_tcp_server(self):
        """TCP 서버를 시작합니다."""
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.bind((self.host, self.port))
            tcp_socket.listen(5)
            tcp_socket.settimeout(1.0)  # 1초 타임아웃
            
            print(f"TCP 서버가 {self.host}:{self.port}에서 시작되었습니다.")
            
            while self.running:
                try:
                    client_socket, addr = tcp_socket.accept()
                    # 새 스레드에서 클라이언트 처리
                    client_thread = threading.Thread(
                        target=self.handle_tcp_client, 
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"TCP server error: {e}")
                    break
            
            tcp_socket.close()
            print("TCP 서버가 종료되었습니다.")
            
        except Exception as e:
            print(f"TCP 서버 시작 실패: {e}")
    
    def start(self):
        """서버를 시작합니다."""
        if self.running:
            print("서버가 이미 실행 중입니다.")
            return
        
        self.running = True
        
        # UDP 서버 스레드
        udp_thread = threading.Thread(target=self.start_udp_server)
        udp_thread.daemon = True
        udp_thread.start()
        
        # TCP 서버 스레드
        tcp_thread = threading.Thread(target=self.start_tcp_server)
        tcp_thread.daemon = True
        tcp_thread.start()
        
        print(f"Debug Syslog 서버가 {self.host}:{self.port}에서 실행 중입니다.")
        print("Ctrl+C를 눌러 종료하세요.")
    
    def stop(self):
        """서버를 중지합니다."""
        self.running = False
        print("\n서버 종료 중...")
    
    def get_received_messages(self):
        """받은 메시지 목록을 반환합니다."""
        return self.received_messages.copy()
    
    def clear_messages(self):
        """받은 메시지를 초기화합니다."""
        self.received_messages.clear()
        print("받은 메시지가 초기화되었습니다.")
    
    def print_statistics(self):
        """통계를 출력합니다."""
        total = len(self.received_messages)
        udp_count = len([m for m in self.received_messages if m['protocol'] == 'UDP'])
        tcp_count = len([m for m in self.received_messages if m['protocol'] == 'TCP'])
        
        print(f"\n=== 통계 ===")
        print(f"총 받은 메시지: {total}")
        print(f"UDP 메시지: {udp_count}")
        print(f"TCP 메시지: {tcp_count}")


def main():
    """메인 함수"""
    server = DebugSyslogServer()
    
    try:
        server.start()
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        server.stop()
        server.print_statistics()
        
        # 받은 메시지 저장
        if server.received_messages:
            import json
            with open("received_messages.json", "w", encoding="utf-8") as f:
                json.dump(server.received_messages, f, ensure_ascii=False, indent=2)
            print(f"받은 메시지가 'received_messages.json'에 저장되었습니다.")


if __name__ == "__main__":
    main()