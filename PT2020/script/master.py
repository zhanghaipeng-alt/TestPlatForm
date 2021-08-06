import zmq.green as zmq
import sys
import random
from gevent.pool import Group
import time
import gevent
import json
from multiprocessing import Queue

#定义两个长度为100的多线程队列
CMD_queue = Queue(maxsize=100)
Result_queue = Queue(maxsize=100)

class Master(object):
    Clients = []
    def __init__(self, cmd_queue, result_queue):
        context = zmq.Context()
        self.cmd_queue = cmd_queue
        self.result_queue = result_queue
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind('tcp://192.168.31.225:6666')
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind('tcp://192.168.31.225:6667')


    def listener(self):
        '''
        主机监听slave机发来的消息，端口6666
        :return:
        '''
        while True:
            msg = self.receiver.recv().decode('utf-8')
            #字符串转字典，反序列化
            msg = json.loads(msg)
            if msg.get('type') == 'ready':
                for i in range(len(Master.Clients)):
                    if msg.get('client_id') == Master.Clients[i].get('client_id'):
                        Master.Clients[i] = msg
                        break
                else:
                    Master.Clients.append(msg)
            # print(Master.Clients)

    def cmd(self):
        while True:
            if not self.cmd_queue.empty():
                cmd_dic = self.cmd_queue.get()
                #判断如果指令的type
                if cmd_dic.get('type') == 'get_clients':
                    self.result_queue.put(Master.Clients)
                elif cmd_dic.get('type') == 'send_script':
                    self.sender.send_string(cmd_dic)
                    self.result_queue.put({'type': 'sent_script', 'result': 'OK'})


            # self.sender.send_string(str(random.randint(1, 3)))
            # time.sleep(2)
            gevent.sleep(1)



def start_master(cmd_queue, result_queue):
    master = Master(cmd_queue=cmd_queue, result_queue=result_queue)
    greenlet = Group()
    greenlet.spawn(master.listener)
    greenlet.spawn(master.cmd)
    greenlet.join()

# if __name__ == '__main__':
#     master = Master()
#     greenlet = Group()
#     greenlet.spawn(master.listener())
#     greenlet.spawn(master.cmd())
#     greenlet.join()

