from locust import HttpUser, TaskSet, task
import psutil
import socket

# 定义用户行为： 相当于取样器
class UserBehavior(TaskSet):
    @task
    def baidu_index(self):
        self.client.get('/')


# 压测场景测试：设置线程组配置
class WebsiteUser(HttpUser):
    task_set = [UserBehavior]
    min_wait = 3000
    max_wait = 6000

class TestPsUtil():

    def test_psutil(self):
        print(psutil.cpu_count())


if __name__ == '__main__':
    print(socket.gethostbyname(socket.gethostname()))