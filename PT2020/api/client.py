'''
    创建client对象
    使用allure装饰器：allure.step 可以在allure报告中将执行的函数作为步骤现实在执行结果中。
    allure.step()还可以添加文字注释，会在报告中展示。
    报告定制：使用allure的attach功能给结果添加报告详细步骤，在send函数中获取发送的详细信息和响应详情

    traceback包，可以捕捉到最近的代码的错误堆栈信息。有两种方法：
        print_exc()直接输出；format_exc()输出字符串
    allow_redirects=False,参数表示是否重定向
'''
import requests
import traceback
import json
import jsonpath

# 创建一个全局变量，用来存放日志信息
infos = []

# 创建一个添加日志信息的方法,cid：测试用例编号，detail：将测试步骤结果加入
def log(cid, result=None, info=None, error=None, detail=None):
    # info中有日志信息，更新。cid是唯一键
    for i in infos:
        if i['id'] == cid:
            if result is not None:
                i['result'] = result
            if info is not None:
                i['log'].append(info)
            if error is not None:
                i['error'].append(error)
            if detail is not None:
                i['detail'].append(detail)
            break
    # infos中没有日志信息，新增。
    else:
        dic = {'id': cid, 'log': [], 'error': [], 'detail': []}
        if result is not None:
            dic['result'] = result
        if info is not None:
            dic['log'].append(info)
        if error is not None:
            dic['error'].append(error)
        if detail is not None:
            dic['detail'].append(detail)
        infos.append(dic)


# 定义一个装饰器方法，在检查点函数中添加装饰器
def add_log(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            log(cid=args[0].cid, error=traceback.format_exc())
            args[0].flag += 1
    return wrapper

#创建一个Client类
class Client(object):

    def __init__(self, cid, url, method, body_type=None, timeout=3, params=None):
        '''
        :param cid: 测试用例编号
        :param url: 接口地址
        :param method: 请求方法
        :param body_type: 请求参数方式
        :param timeout: 超时时间
        :param params: get请求时参数列表
        '''
        self.cid = cid
        self.url = url
        self.method = method
        self.body_type = body_type
        self.timeout = timeout
        self.params = params
        self.res = None
        self.headers = {}
        self.data = {}

        #定义一个测试用例执行结果计数
        self.flag = 0

    def set_header(self, key, value):
        self.headers[key] = value

    def set_headers(self, data):
        if isinstance(data, dict):
            self.headers = data
        else:
            raise Exception('请求头必须是字典格式！')

    def set_body(self, key, value):
        self.data[key] = value

    def set_bodies(self, data):
        if isinstance(data, dict):
            self.data = data
        else:
            raise Exception('参数必须是字典格式')

    # 获取响应头
    @property
    def res_headers(self):
        if self.res is not None:
            return self.res.headers
        else:
            # print('未获取到响应头')
            return None

    # 获取响应cookies
    @property
    def res_cookies(self):
        if self.res is not None:
            return self.res.cookies
        else:
            # print('响应为空，未获取到cookies')
            return None

    # 获取响应内容
    @property
    def res_content(self):
        if self.res is not None:
            return self.res.content
        else:
            # print('响应内容为空')
            return None

    # 获取响应状态码
    @property
    def res_status_code(self):
        if self.res is not None:
            return  self.res.status_code
        else:
            # print('响应状态码为空')
            return None

    # 获取响应时间
    @property
    def res_times(self):
        if self.res is not None:
            return self.res.elapsed.total_seconds()*1000
        else:
            # print('相应内容为空值，未获取到响应时间')
            return None

    # 获取响应的json格式
    @property
    def res_to_json(self):
        if self.res is not None:
            return self.res.json()
        else:
            return None

    # 或许xpath表达式内容值
    def res_content_json_path(self, path):
        if path.startswith('$.'):
            path = '$.' + path
        result = jsonpath.jsonpath(self.res_to_json, path)
        if result:
            return result[0]
        else:
            return None

    # 检查点：响应状态码是否是200
    @add_log
    def check_status_code_200(self):
        assert self.res_status_code == 200,  f'响应状态码检查失败，预期结果是200，实际结果是{self.res_status_code}'
        log(cid=self.cid, info='响应状态码检查成功,状态码为200！')

    # 检查点：判断实际响应状态
    @add_log
    def check_status_code(self, code):
        assert self.res_status_code == code, f'响应状态码检查失败，预期结果为{code}, 实际结果为{self.res_status_code}'
        log(cid=self.cid, info='响应状态码检查成功！')

    # 检查点：判断响应时间是否小于预期值
    @add_log
    def check_respond_time(self, times):
        assert self.res_times < times, f'响应时间检查失败，预期响应时间为小于{times}, 实际响应时间为{self.res_times}'
        log(cid=self.cid, info='响应时间检查成功!')

    # 检查点：判断响应结果中包含预期字符串
    @add_log
    def check_respond_content(self, content):
        assert content in self.res_content, f'响应内容检查失败，预期结果为响应中包含{content}, 实际结果为{self.res_content}'
        log(cid=self.cid, info='响应结果检查成功')

    # 检查点:验证响应中包含某节点值
    @add_log
    def check_respond_json_content(self, path, content):
        result = self.res_content_json_path(path=path)
        if result is not None:
            assert result == content, f'响应内容检查失败，预期响应中{path}的值为{content}, 实际的值为{result}'
            log(cid=self.cid, info=f'响应结果检查成功，包含预期值{content}！')
        else:
            assert False, f'响应内容获取失败，无{content}'

    # 检查点：验证响应头中包含预期值
    @add_log
    def check_respond_header_content(self, value):
        assert value in self.res_headers, f'响应头验证失败，预期结果包含{value}, 实际结果为{self.res_headers}'
        log(cid=self.cid, info='响应头中包含预期值！')

    # 发送一个请求
    def send(self):
        try:
            if self.method == 'get':
                self.res = requests.get(url=self.url, headers=self.headers, params=self.params, timeout=self.timeout)

            elif self.method == 'post':
                if self.body_type == 'form':
                    self.set_header('Content-Type', 'application/x-www-form-urlencoded')
                    self.res = requests.post(url=self.url, headers=self.headers, data=self.data, params=self.params,
                                             timeout=self.timeout, allow_redirects=False)
                elif self.body_type == 'file':
                    self.res = requests.post(url=self.url, headers=self.headers, params=self.params,
                                             files=self.data, timeout=self.timeout, allow_redirects=False)
                elif self.body_type == 'json':
                    self.set_header('Content-Type', 'application/json')
                    self.res = requests.post(url=self.url, headers=self.headers, params=self.params,
                                             timeout=self.timeout, allow_redirects=False,json=self.data)
                else:
                    log(cid=self.cid, result='skip', error='请求正文格式错误，未发送')
        except:
            log(cid=self.cid, error='请求发送失败\n'+ traceback.format_exc())
        finally:
            # 将每一步的详细结果加入到detail中
            log(cid=self.cid, detail='请求URL：' + self.url)
            log(cid=self.cid, detail='请求方式：' + self.method)
            log(cid=self.cid, detail='请求头：' + json.dumps(self.headers))
            log(cid=self.cid, detail='请求正文：' + json.dumps(self.data))
            if self.res_status_code:
                log(cid=self.cid, detail='响应状态码：' + str(self.res_status_code))
            else:
                log(cid=self.cid, detail='响应状态码：' + 'None')
                log(cid=self.cid, detail='响应正文' + 'None')


    class METHOD():
        POST = 'post'
        GET = 'get'

    class BODY_TYPE():
        FORM = 'form'
        JSON = 'json'
        FILE = 'file'




