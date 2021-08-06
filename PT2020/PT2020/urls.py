"""PT2020 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('project/', views.project),
    path('api/project/delete/', views.api_project_delete),
    path('api/project/edit/', views.api_project_edit),
    path('api/project/new/', views.api_project_new),
    path('api/', views.api),
    path('api/single_new/', views.single_new),
    path('api/add/', views.api_add),
    path('api/upload/', views.api_upload),
    path('api/get_infos/', views.api_table),
    path('case/new/', views.case_new),
    path('api/case/new/', views.api_new_case),
    path('case/list/', views.case_list),
    path('api/case/get_caseinfo/', views.api_get_caseinfo),
    path('case/single_run/', views.case_single_run),
    path('task/list/', views.task_list),
    path('task/new/', views.task_new),
    path('task/api/new/', views.task_api_new),
    path('task/get_info/', views.task_info),
    path('task/run/', views.task_run),
    path('test/', views.testView, name='testView'),
    path('data/viewData/info', views.viewData),
    path('api/data/userInfo/', views.getUserInfo),
    path('api/data/userDefault/', views.getUserDefault),
    path('locust/', views.locust),
    path('api/locust/upload', views.api_locust_upload)
]
