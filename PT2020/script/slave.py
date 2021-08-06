import zmq.green as zmq
import sys
import gevent
import socket
import time
import psutil
import json
from gevent.pool import Group
import os

class Slave(object):

    def __init__(self, ip, port):
        self.client_id = socket.gethostbyname(socket.gethostname())
        self.status = 'ready'
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        try:
            self.receiver.connect(f'tcp://{ip}:{port+1}')
        except:
            sys.exit(0)

        self.sender = context.socket(zmq.PUSH)
        try:
            self.sender.connect(f'tcp://{ip}:{port}')
        except:
            sys.exit(0)

    def listener(self):
        '''
        定义一个监听的方法，监听主机的端口发过来的命令
        :return:
        '''
        while True:
            msg = self.receiver.recv().decode('utf-8')
            print(msg)

    def send(self, msg):
        '''
        定义一个发送消息的方法，将slave机器的状态信息发送给主机
        :param msg:
        :return:
        '''
        while True:
            self.sender.send(msg)
            gevent.sleep(2)

    def worker(self):
        '''
        定义一个worker方法，接受主机指令并执行，然后将结果上报给主机
        :return:
        '''
        while True:
            msg = self.receiver.recv().decode('utf-8')
            msg = json.loads(msg)
            if msg.get('type') == 'send_script':
                if not os.path.exists('./script/demo/'):
                    os.mkdir('./script/demo/')
                file_name = os.path.join('./script/demo/', msg.get('file_name'))
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(msg.get('stream'))
            elif msg.get('type') == 'stop':
                pass
                self.send('msg')

    def ready_loop(self):
        '''
        循环上报系统信息
        :return:
        '''
        while True:
            data = {}
            data['client_id'] = self.client_id
            data['type'] = 'ready'
            data['time'] = time.time()
            data['status'] = self.status
            performance_info = {}
            performance_info['cpu_core'] = psutil.cpu_count()
            performance_info['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            performance_info['mem_percent'] = psutil.virtual_memory().percent
            performance_info['mem_free'] = round(psutil.virtual_memory().free/1024**2, 2)

            data['data'] = performance_info
            self.sender.send_string(json.dumps(data, ensure_ascii=False))

            gevent.sleep(3)

if __name__ == '__main__':
    slave = Slave('192.168.31.225', 6666)
    greenlet = Group()
    greenlet.spawn(slave.worker)
    greenlet.spawn(slave.ready_loop)
    greenlet.join()
