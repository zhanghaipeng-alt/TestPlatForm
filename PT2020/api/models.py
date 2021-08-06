from django.db import models

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=20, unique=True, null=False, db_column='title')
    desc = models.CharField(max_length=50, null=False)
    owner = models.CharField(max_length=50, db_column='base_url')

class ApiInfo(models.Model):
    name = models.CharField(max_length=20, unique=True, null=False)
    desc = models.CharField(max_length=50, null=True)
    url = models.URLField(null=False)
    method = models.IntegerField(choices=((0, 'GET'), (1, 'POST')), default=0)
    body_type = models.IntegerField(choices=((0, 'None'), (1, 'URL-ENCODE'), (2, 'JSON')), default=0)
    header = models.TextField(null=True)
    body = models.TextField(null=True)
    update_time = models.DateTimeField(null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class CaseInfo(models.Model):
    name = models.CharField(max_length=50, null=False)
    desc = models.CharField(max_length=50)
    header = models.TextField(null=True)
    body = models.TextField(null=True)
    update_time = models.DateTimeField(null=False)
    depends = models.TextField(null=True)
    depens_infos = models.TextField(null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    api = models.ForeignKey(ApiInfo, on_delete=models.CASCADE)
    checks = models.TextField(null=True)
    check_code = models.IntegerField(default=200)

class TaskInfo(models.Model):
    name = models.CharField(max_length=30, null=False, unique=True)
    desc = models.TextField(null=True)
    update_time = models.DateTimeField(null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    case = models.ManyToManyField(CaseInfo)

class ResultInfo(models.Model):
    number = models.CharField(max_length=30, unique=True, null=False)
    report_url = models.TextField(null=True)
    status = models.IntegerField(choices=((1, '执行中'), (1, '已结束')), default=0)
    update_time = models.DateTimeField(null=False)
    task = models.ForeignKey(TaskInfo, on_delete=models.CASCADE)


