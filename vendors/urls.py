from django.urls import path, include
from rest_framework import routers
from .views import BaiDuWordOCRView


urlpatterns = [
    path('baidu/wordocr', BaiDuWordOCRView.as_view(), name='baidu_wordocr'),
]
