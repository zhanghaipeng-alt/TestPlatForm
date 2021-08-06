import xlrd
from api.models import *
import time


def sava_excel(data, pid, over):
    '''
    从Excel导入测试用例
    :param data:
    :param pid:
    :param over:
    :return:
    '''
    faile = 0
    success = 0
    for api in data:
        name = api.get('接口名称')
        desc = api.get('描述')
        url = api.get('地址')
        method = api.get('方法类型', 0)
        body_type = api.get('参数类型', 0)
        headers = api.get('请求头')
        body = api.get('参数')
        update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if method == 'GET':
            method = 0
        elif method == 'POST':
            method = 1

        if body_type == 'NONE':
            body_type = 0
        elif body_type == 'URL-ENCODE':
            body_type = 1
        elif body_type == 'JSON':
            body_type = 2
        if name not in ['', None] and url not in ['', None] and method not in ['', None] and body_type not in ['', None]:
            if Project.objects.filter(id=int(pid)).exists():
                if not ApiInfo.objects.filter(name=name).exists():
                    ApiInfo.objects.create(
                        name=name,
                        desc=desc,
                        url=url,
                        method=method,
                        body_type=body_type,
                        header=headers,
                        body=body,
                        update_time=update_time,
                        project_id=int(pid)
                    )
                    success += 1
                else:
                    if over == 0:
                        continue
                    elif over == 1:
                        ApiInfo.objects.filter(name=name).update(
                            name=name,
                            desc=desc,
                            method=method,
                            body_type=body_type,
                            header=headers,
                            body=body,
                            update_time=update_time,
                            project_id=int(pid)
                        )
                        success += 1
            else:
                return {"code": 1, "msg": "项目不存在"}
        else:
            faile += 1
    return {"code": 0, "msg": "本次成功导入用例{success}个，导入失败{faile}个".format(success=success, faile=faile)}




def parse_excel(filename, pid, over):
    '''
    打开Excel文件；
    参数：
        over：确定是否跳过
    :return:
    '''
    data = []
    try:
        workbook = xlrd.open_workbook('./upload/' + filename)
        sheet = workbook.sheet_by_index(0)
        header = sheet.row_values(0)
        for i in range(1, sheet.nrows):
            dic = {}
            for index, value in enumerate(sheet.row_values(i)):
                dic[header[index]] = value
            data.append(dic)
        result = sava_excel(data, pid, over)
        return result
    except xlrd.biffh.XLRDError:
        return {"code": 1, "msg": "sheet页不存在"}
    except FileNotFoundError:
        return {"code": 1, "msg": "服务异常"}


