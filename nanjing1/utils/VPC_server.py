import socket
import threading
import time
import logging
from queue import Queue

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TCPServer:
    def __init__(self, host='192.168.18.15', port=50001):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False
        self.lock = threading.Lock()
        self.is_detecting = False  # 是否处于检测状态
        self.detection_requested = False  # 新增：是否收到检测请求的标志位
        self.waiting_for_ack = False
        self.current_result = None
        self.retry_thread = None
        self.ack_received = threading.Event()
        
    def start(self):
        """启动服务器"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        
        logging.info(f"VPC Server started on {self.host}:{self.port}")
        
        server_thread = threading.Thread(target=self._accept_connections)
        server_thread.daemon = True
        server_thread.start()
        
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
                
    def has_detection_request(self):
        """检查是否有检测请求"""
        return self.detection_requested
        
    def clear_detection_request(self):
        """清除检测请求标志"""
        self.detection_requested = False
                
    def _accept_connections(self):
        """接受PLC的连接"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_socket.settimeout(60)
                    
                    if self.client_socket:
                        try:
                            self.client_socket.close()
                        except:
                            pass
                            
                    self.client_socket = client_socket
                    self.client_address = client_address
                    logging.info(f"PLC connected from {client_address}")
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
            except Exception as e:
                logging.error(f"Error in accept_connections: {e}")
                time.sleep(1)
                
    def _handle_client(self, client_socket, client_address):
        """处理PLC客户端通信"""
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8').strip()
                logging.info(f"Received from PLC: {message}")
                
                if message == "@@@GOODS_ARV1!!!":
                    if self.is_detecting:
                        response = "@@@ARV1TASK_ERR!!!"
                    else:
                        response = "@@@ARV1TASK_ST!!!"
                        self.is_detecting = True
                        self.detection_requested = True  # 设置检测请求标志
                    client_socket.send(response.encode('utf-8'))
                    
                elif message == "@@@RCOK!!!":
                    logging.info("PLC confirmed receipt of detection result")
                    self.waiting_for_ack = False
                    self.ack_received.set()
                    self.is_detecting = False
                    self.detection_requested = False  # 清除检测请求标志
                    
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"Error handling client {client_address}: {e}")
                break
                
        if self.client_socket == client_socket:
            self.client_socket = None
            self.client_address = None
        try:
            client_socket.close()
        except:
            pass
        logging.info(f"PLC {client_address} disconnected")
            
    def _retry_send_result(self, result):
        """重试发送结果的线程函数"""
        while self.waiting_for_ack and self.running:
            try:
                if self.client_socket:
                    self.client_socket.send(result.encode('utf-8'))
                    logging.info(f"Sent detection result: {result}")
                    
                if self.ack_received.wait(timeout=3.0):  # 等待确认，超时3秒
                    break
                self.ack_received.clear()
                logging.info("No acknowledgment received, retrying...")
                
            except Exception as e:
                logging.error(f"Error in retry send: {e}")
                break
                
    def send_detection_result(self, result):
        """发送检测结果到PLC，带重试机制"""
        if not self.client_socket:
            logging.error("No PLC connected")
            return False
            
        if not self.is_detecting:
            logging.warning("Not in detection state")
            return False
            
        self.current_result = result
        self.waiting_for_ack = True
        self.ack_received.clear()
        
        # 启动重试线程
        if self.retry_thread and self.retry_thread.is_alive():
            self.waiting_for_ack = False
            self.ack_received.set()
            self.retry_thread.join()
            
        self.retry_thread = threading.Thread(
            target=self._retry_send_result,
            args=(result,)
        )
        self.retry_thread.daemon = True
        self.retry_thread.start()
        return True

# 创建全局VPC服务器实例
vpc_server = None

if __name__=="__main__":
    # 创建并启动服务器
    vpc_server = TCPServer()
    vpc_server.start()
    
    # 示例：外部代码如何使用检测标志位
    try:
        while True:
            if vpc_server.has_detection_request():
                # 执行检测逻辑
                logging.info("Detection requested, performing detection...")
                # 这里可以调用你的检测接口
                result = "@@@DIR000;Type:0103!!!"
                vpc_server.send_detection_result(result)
                vpc_server.clear_detection_request()  # 清除检测请求标志
            time.sleep(0.1)  # 短暂睡眠避免CPU占用过高
    except KeyboardInterrupt:
        vpc_server.stop()