from django.urls import path
from .views import InsuranceInfoView, TaskHeiNiuView


urlpatterns = [
    path('insurance', InsuranceInfoView.as_view()),  # 保险协议
    path('task/heiniu/<int:id>', TaskHeiNiuView.as_view(), name='task_heiniu'),
    ]
