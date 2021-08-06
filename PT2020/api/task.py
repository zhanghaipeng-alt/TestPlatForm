from celery import shared_task
import time


@shared_task
def task_test(tmp):
    # 执行的步骤提示
    # 1.在tasinfo数据库中读取任务ID
    # 2.根据任务ID在相关数据库表中读取接口信息
    # 3.执行测试用例
    # 4.出测试报告
    # 5.测试结果入库
    time.sleep(10)
    with open(f'./api/static/report/{tmp}.html', 'wb') as f:
        pass

    # 执行保存测试结果入库：ReportInfo.objects.create{}
    print('============')