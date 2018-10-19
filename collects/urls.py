from django.urls import path
from .views import CollectModelView, TaskDongFangView, TaskHeiNiuView, HNCollectModeView, LongFenQiView

urlpatterns = [
    path('collect', CollectModelView.as_view()),
    path('hncollect', HNCollectModeView.as_view()),
    path('longfenqi', LongFenQiView.as_view()),
    path('task/dongfang/<int:id>', TaskDongFangView.as_view(), name='task_dongfang'),
    path('task/heiniu/<int:id>', TaskHeiNiuView.as_view(), name='task_heiniu'),
]
