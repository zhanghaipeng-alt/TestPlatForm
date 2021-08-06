from django.shortcuts import render
from api.models import *
from django.http import *
import json
import time
from api.util import *
from api.client import *
from api.task import *
from api.database import *
import script.master as master
from script.master import CMD_queue, Result_queue
import multiprocessing



# Create your views here.

def index(request):
    return render(request, 'base.html')

def project(request):
    projects = Project.objects.all()
    return render(request, 'project.html', {"projects": projects})

def api_project_delete(request):
    '''
    删除项目
    :param request:
    :return:
    '''
    pid = request.GET.get('pid')

    if pid not in [None, '']:
        try:
            pid = int(pid)
            if Project.objects.filter(id=pid).exists():
                Project.objects.filter(id=pid).delete()
                return JsonResponse({"code": 0, "msg": "删除成功!"})
            else:
                return JsonResponse({"code": 1, "msg": "项目不存在！"})
        except:
            return JsonResponse({"code": 1, "msg": "程序错误"})
    else:
        return JsonResponse({"code": 1, "msg": "没有此项目！"})

def api_project_edit(request):
    '''
    编辑项目接口
    :param request:
    :return:
    '''
    pid = request.POST.get('pid')
    title = request.POST.get('title')
    desc = request.POST.get('desc')
    base_url = request.POST.get('base_url')

    if pid not in [None, ''] and title not in [None, '']:
        project = Project.objects.filter(id=int(pid))
        if project.exists():
            project = project.first()

            if project.name == title:
                project.desc = desc
                project.owner = base_url
                project.save()
                return JsonResponse({"code": 0, "msg": "项目编辑成功"})
            else:
                if not Project.objects.filter(name=title).exists():
                    project.name = title
                    project.desc = desc
                    project.owner = base_url
                    project.save()
                    return JsonResponse({"code": 0, "msg": "项目编辑成功"})
                else:
                    return JsonResponse({"code": 1, "msg": "项目已存在"})

        else:
            return JsonResponse({"code": 1, "msg": "项目不存在！"})

    else:
        return JsonResponse({"code": 1, "msg": "参数错误"})

def api_project_new(request):
    '''
    新增一个项目
    :param request:
    :return:
    '''
    title = request.POST.get('title')
    desc = request.POST.get('desc')
    base_url = request.POST.get('base_url')

    if title not in [None, '']:
        try:
            project = Project.objects.filter(name=title)
            if not project.exists():
                Project.objects.create(name=title, desc=desc, owner=base_url)
                return JsonResponse({"code": 0, "msg": "新增成功"})
            else:
                return JsonResponse({"code": 1, "msg": "项目已存在"})
        except Exception as e:
            print(e)

    else:
        return JsonResponse({"code": 1, "msg": "参数错误"})

def api(request):
    pid = request.GET.get('pid')

    project = Project.objects.all()
    apis = ApiInfo.objects.all()
    print(pid, type(pid))
    if pid not in ['', None]:
        project = project.filter(id=int(pid))
        apis = apis.filter(project_id=int(pid))
        return render(request, 'api1.html', {"project": project.first(), "apis": apis})
    else:
        return render(request, 'api1.html', {"project": project, "apis": apis})



def single_new(request):
    '''
    返回一个新增接口页面
    :param request:
    :return:
    '''
    pid = request.GET.get('pid')
    if pid not in ['', None]:
        project = Project.objects.filter(id=int(pid))
        if project.exists():
            return render(request, 'api_new1.html', {"project": project.first()})
        else:
            return render(request, 'api_new1.html', {"project": None})
    else:
        return render(request, 'api_new1.html', {"project": None})

def api_add(request):
    '''
    提交一个新增接口具体值
    :param request:
        pid : 项目编号
        name : 接口名称
        desc : 接口描述
        URL : 接口地址
        header_key: 头信息主键
        header_value: 头信息值
        method: 请求方法
        body_type: 正文体格式
        body_content: 正文内容
    :return:
    '''

    pid = request.POST.get('pid')
    name = request.POST.get('name')
    desc = request.POST.get('desc')
    url = request.POST.get('url')
    header_key = request.POST.getlist('header_key')
    header_value = request.POST.getlist('header_value')
    method = request.POST.get('method')
    body_type = request.POST.get('body-type')
    body = request.POST.get('body')
    # print(pid, name, desc, url, header_key, header_value, method, body_type, body)
    if pid not in [None, ''] and name not in [None, ''] and url not in [None, ''] and method not in [None, ''] and body_type not in [None, '']:
        project = Project.objects.filter(id=int(pid))
        if project.exists():
            if not ApiInfo.objects.filter(name=name).exists():

                header_dict = {}
                for k, v in zip(header_key, header_value):
                    if k not in [None, '']:
                        header_dict[k] = v
                    else:
                        continue
                try:
                    headers = json.dumps(header_dict)
                except:
                    return JsonResponse({"code": 1, "msg": "头信息参数格式错误"})
                print(headers)
                ApiInfo.objects.create(
                    name=name,
                    url=url,
                    desc=desc,
                    method=int(method),
                    body_type=int(body_type),
                    header=headers,
                    body=body,
                    update_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                    project_id=int(pid)
                )
                return JsonResponse({"code": 0, "msg": "新增成功！"})
            else:
                return JsonResponse({"code": 1, "msg": "接口已存在"})
        else:
            return JsonResponse({"code": 1, "msg": "项目不存在"})
    else:
        return JsonResponse({"code": 1, "msg": "缺少必要参数"})

def api_upload(request):
    '''
    上传一个Excel文件
    :param request:
    :return:
    '''

    pid = request.POST.get('pid')
    over = request.POST.get('over')
    file = request.FILES.get('file')
    if pid not in [None, ''] and over not in [None, ''] and file is not None:
        if file.name.endswith('.xlsx'):
            temp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            with open('./upload/' + temp + file.name, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            result = parse_excel(temp + file.name, pid, over)
            return JsonResponse(result)
        else:
            return JsonResponse({"code": 1, "msg": "上传文件的格式错误"})
    else:
        return JsonResponse({"code": 1, "msg": "参数不全"})

def api_table(request):
    '''
    获取接口信息
    :param request:
    :return:
    '''
    pid = request.GET.get('pid')
    page = int(request.GET.get('page'))
    limit = int(request.GET.get('limit'))
    kw = request.GET.get('kw')
    method = request.GET.get('method')


    apis = ApiInfo.objects.all()
    if pid not in ['', None]:
        apis = ApiInfo.objects.filter(project_id=int(pid))
    if method not in ['', None]:
        apis = ApiInfo.objects.filter(method__contains=int(method))
    if kw not in ['', None]:
        apis = ApiInfo.objects.filter(name__contains=kw)
    data = []
    for api in apis:
        if api.method == 0:
            method = 'GET'
        elif api.method == 1:
            method = 'POST'
        else:
            method = 'NONE'
        data.append({"id": api.id, "name": api.name, "method": method, "url": api.url, "update_time": api.update_time.strftime("%Y-%m-%d %H:%M:%S")})
        # print(api.update_time)
    # 实现页面的分页功能
    count = len(data)
    data = data[(page-1)*limit : page*limit]

    print(data, type(data), count)
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data})

def case_new(request):
    '''
    测试用例新增页面
    :param request:
    :return:
    '''
    pid = request.GET.get('pid')
    aid = request.GET.get('aid')
    project = None
    api = None
    header = {}
    if pid not in ['', None]:
        p = Project.objects.filter(id=int(pid))
        if p.exists():
            project = p.first()
    if aid not in ['', None]:
        a = ApiInfo.objects.filter(id=int(aid))
        if a.exists():
            api = a.first()
            try:
                header = json.loads(api.header)
            except Exception as e:
                print(e)
    return render(request, 'case_new1.html', {"project": project, "api": api, "header": header})

def api_new_case(request):
    '''
    新增测试用例
    :param request:
    :return:
    '''
    pid = request.POST.get('pid')
    aid = request.POST.get('aid')
    name = request.POST.get('caseName')
    desc = request.POST.get('caseDesc')
    header_key = request.POST.getlist('header_key')
    header_value = request.POST.getlist('header_value')
    body = request.POST.get('body')
    status_code = request.POST.get('status-code')
    json_path = request.POST.getlist('assert-key')
    json_value = request.POST.getlist('assert-value')
    if pid not in ['', None] and aid not in ['', None] and name not in ['', None]:
        if Project.objects.filter(id=int(pid)).exists():
            if ApiInfo.objects.filter(id=int(aid)).exists():
                if not CaseInfo.objects.filter(name=name).exists():
                    header_dict = {}
                    for k, v in zip(header_key, header_value):
                        if k not in ['', None]:
                            header_dict[k] = v
                        else:
                            continue
                    try:
                        headers = json.dumps(header_dict)
                    except:
                        return JsonResponse({"code": 1, "msg": "头信息参数格式错误"})

                    json_dict = {}
                    for m, n in zip(json_path, json_value):
                        if m not in ['', None]:
                            json_dict[m] = n
                        else:
                            continue
                    try:
                        json_values = json.dumps(json_dict)
                    except Exception as e:
                        return JsonResponse({"code": 1, "msg": f"检查点格式错误, {e}"})
                    print(headers)
                    CaseInfo.objects.create(
                        name=name,
                        desc=desc,
                        header=headers,
                        body=body,
                        update_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                        project_id=int(pid),
                        api_id=int(aid),
                        checks=json_values,
                        check_code=int(status_code)
                    )
                    return JsonResponse({"code": 0, "msg": "新增用例成功"})
                else:
                    return JsonResponse({"code": 1, "msg": "用例已存在"})
            else:
                return JsonResponse({"code": 1, "msg": "关联的接口不存在"})
        else:
            return JsonResponse({"code": 1, "msg": "关联项目不存在"})
    else:
        return JsonResponse({"code": 1, "msg": "缺少必要参数"})

def case_list(request):
    '''
    返回测试用例列表页面
    :param request:
    :return:
    '''
    pid = request.GET.get('pid')
    project = Project.objects.all()
    if pid not in ['', None]:
        project = project.filter(id=int(pid))
        if project.exists():
            return render(request, 'case1.html', {"project": project.first()})
        else:
            return render(request, 'case1.html', {"project": None, "msg": "项目不存在"})
    else:
        return render(request, 'case1.html', {"project": project})

def api_get_caseinfo(request):
    '''
    获取测试用例接口
    :param request:
    :return:
    '''
    pid = request.GET.get('pid')
    kw = request.GET.get('kw')
    page = int(request.GET.get('page'))
    limit = int(request.GET.get('limit'))

    cases = CaseInfo.objects.all()
    if pid not in ['', None]:
        cases = CaseInfo.objects.filter(project_id=int(pid))
    if kw not in ['', None]:
        cases = CaseInfo.objects.filter(name__contains=kw)
    data = []
    for case in cases:
        data.append({"id": case.id, "name": case.name, "api_name": case.api.name, "update_time": case.update_time.strftime("%Y-%m-%d %H:%M:%S")})

    count = len(data)
    data = data[(page - 1) * limit: page * limit]
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data})

def case_single_run(request):
    '''
    单条用例执行
    :param request:
    :return:
    '''
    cid = request.POST.get('cid')

    if cid not in ['', None]:
        case = CaseInfo.objects.filter(id=int(cid))
        if case.exists():
            case = case.first()
            header = json.loads(case.header)
            body = json.loads(case.body)
            url = case.api.url
            method = case.api.method
            body_type = case.api.body_type
            code = case.check_code
            if method == 0:
                method = 'get'
            elif method == 1:
                method = 'post'
            else:
                method = 'get'

            if body_type == 0:
                body_type = None
            elif body_type == 1:
                body_type = 'form'
            elif body_type == 2:
                body_type = 'json'
            else:
                body_type = None
            try:
                client = Client(cid=cid, url=url, body_type=body_type, method=method)
            except Exception as e:
                return JsonResponse({"code": 1, "msg": e})
            try:
                client.set_headers(header)
                client.set_bodies(body)
                client.send()
                status_code = client.res_status_code
                content = client.res_content
            except:
                return JsonResponse({"code": 1, "status_code": status_code, "content": (str(content, 'utf-8')), "msg": "发送失败"})
            if status_code == code:
                return JsonResponse({"code": 0, "status_code": status_code, "content": (str(content, 'utf-8')), "msg": (str(content, 'utf-8'))})
            else:
                return JsonResponse({"code": 1, "status_code": status_code, "content": (str(content, 'utf-8')), "msg": (str(content, 'utf-8'))})
        else:
            return JsonResponse({"code": 1, "msg": "用例不存在"})
    else:
        return JsonResponse({"code": 1, "msg": "参数错误"})

def task_list(request):
    '''
    返回一个任务列表页面
    :param request:
    :return:
    '''
    return render(request, 'task.html')

def task_new(request):
    '''
    返回一个新增任务页面，传回所有的project项目对象
    :param request:
    :return:
    '''
    return render(request, 'task_new.html', {"projects": Project.objects.all()})

def task_api_new(request):
    '''
    新增一个任务，入库
    :param request:
    :return:
    '''
    pid = request.POST.get('pid')
    name = request.POST.get('name')
    desc = request.POST.get('desc')
    cases = request.POST.get('case_number')
    print(pid, name, desc, cases)
    if pid not in ['', None] and name not in ['', None]:
        if Project.objects.filter(id=int(pid)).exists():
            if not TaskInfo.objects.filter(name=name).exists():
                if cases and len(cases.split(',')) > 0:
                    task = TaskInfo.objects.create(name=name,
                                                    desc=desc,
                                                    project_id=int(pid),
                                                    update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                                    )
                    for cid in cases.split(','):
                        case_object = CaseInfo.objects.filter(id=int(cid))
                        if case_object.exists():
                            # 增加一组对应的关联关系
                            task.case.add(case_object.first())
                    return JsonResponse({"code": 0, "msg": "新增测试任务成功"})
                else:
                    return JsonResponse({"code": 1, "msg": "测试用例不能为空"})
            else:
                return JsonResponse({"code": 1, "msg": "任务已存在"})
        else:
            return JsonResponse({"code": 1, "msg": "关联的项目不存在"})
    else:
        return JsonResponse({"code": 1, "msg": "参数错误"})
def task_info(request):
    '''
    获取任务列表
    :param request:
    :return:
    '''
    pid = request.GET.get('pid')
    kw = request.GET.get('kw')
    page = int(request.GET.get('page'))
    limit = int(request.GET.get('limit'))

    tasks = TaskInfo.objects.all()
    if pid not in ['', None]:
        tasks = tasks.filter(project_id=int(pid))
    if kw not in ['', None]:
        tasks = tasks.filter(name__contains=kw)
    data = []
    for task in tasks:
        data.append({"id": task.id, "name": task.name, "project_name": task.project.name,
                     "update_time": task.update_time.strftime('%Y-%m-%d %H-%M-%S')})

    count = len(data)
    data = data[(page-1)*limit : page*limit]
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data})

def task_run(request):
    '''
    执行任务
    :param request:
    :return:
    '''
    tmp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    task_test.delay(tmp)
    return JsonResponse({"code": 0, "msg": f"任务正在执行中！本次任务结果为【{tmp}.html】"})


def testView(request):
    return HttpResponse(content='这是一个测试页面')

def viewData(request):
    return render(request, 'viewdata.html')

def getUserInfo(request):
    '''
    获取用户在b2c系统信息
    :param request:
    :return:
    '''
    mobile = request.GET.get('mobile')
    idno = request.GET.get('idno')
    mysql = ClientDataBase(host='10.1.2.242', port=8066, username='root', password='root123',
                           DATABASE='TIENS_MYCAT')
    print(mobile)

    if mobile not in ['', None] and idno in ['', None]:
        result = mysql.select_user_by_phone(mobile=mobile)
    elif mobile in ['', None] and idno not in ['', None]:
        result = mysql.select_user_by_idno(idno=idno)
    elif mobile not in ['', None] and idno not in ['', None]:
        result = mysql.select_user_by_idandmobile(idno=idno, mobile=mobile)
    elif mobile in ['', None] and idno in ['', None]:
        result = mysql.select_user_by_idandmobile(idno='', mobile='')

    data = []
    for r in result:
        data.append(r)
    count = len(data)


        # data.append({"userID": r.userID, "userTypeID": r.userTypeID, "mobile": r.mobile, "is_bindmobile": is_bindmobile, "status": r.status,
        #              "idno": r.idno, "joyoCode": r.joyoCode, "parentJoyoCode": r.parentJoyoCode, "branchID": r.branchID,
        #              "branchCode": r.branchCode, "name": r.name, "new_nick_name": r.new_nick_name, "staff_id": r.staff_id,
        #              "staff_name": r.staff_name})

    # return JsonResponse({"code:": 0, "msg": "", "count": len(data), "data": data})
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data})

def getUserDefault(request):
    '''
    一个默认的假的返回
    :param request:
    :return:
    '''
    data = [{"userID": "", "userTypeID": "", "mobile": "", "is_bindmobile": "已绑定", "status": "",
             "idno": "", "joyoCode": "", "parentJoyoCode": "", "branchID": "",
             "branchCode": "", "name": "", "new_nick_name": "", "staff_id": "",
             "staff_name": ""}]
    count = len(data)
    return JsonResponse({"code": 0, "count": count, "data": data})


def wait_result():
    '''
    定义一个函数，轮询结果队列，间隔0.5秒，5秒后无结果返回空值
    :return:
    '''
    retry = 0
    while Result_queue.empty():
        time.sleep(0.5)
        retry += 1
        if retry > 10:
            return None
    return Result_queue.get()

def get_clients():
    '''
    函数是获取结果队列中的值，是内部调用函数，所以不使用request参数
    :return:
    '''
    #像指令队列中添加指令，该指令又master主机分配slave机执行（该例子中不用slave执行，master自己执行）
    CMD_queue.put({'type': 'get_clients'})
    r = wait_result()
    if r is not None:
        return r
    else:
        return []

    #等待结果

def send_script(file_name, ip):
    '''
    向节点机发送一个script脚本
    :param file:
    :param ip:
    :return:
    '''
    CMD_queue.put({'type': 'send_script', 'file_name': file_name, 'ip': ip})
    r = wait_result()
    if r is not None:
        return r
    else:
        return []


def locust(request):
    '''
    拿到Clients中的数据，判断系统的更新时间
    :param request:
    :return:
    '''
    clients = get_clients()
    for i in range(len(clients)):
        if time.time() > clients[i]['time'] + 5:
            clients[i]['status'] = 'off-line'
            clients[i]['data']['cpu_percent'] = '-'
            clients[i]['data']['mem_percent'] = '-'
            clients[i]['data']['mem_free'] = '-'

    return render(request, 'locust.html', {"clients": clients})

def api_locust_upload(request):
    '''
    接受节点机上传的script脚本
    :param request:
    :return:
    '''
    script_file = request.FILES.get('script_file')
    ip = request.POST.get('ip')
    if script_file and ip not in ['', None]:
        send_script(file_name=script_file, ip=ip)
        return JsonResponse({})
    else:
        return JsonResponse({})


# 启动一个守护进程
p_master = multiprocessing.Process(target=master.start_master, args=(master.CMD_queue, master.Result_queue))
p_master.daemon = True
p_master.start()




