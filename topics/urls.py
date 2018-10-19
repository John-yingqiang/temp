from django.urls import path, include
from rest_framework import routers
from .views import ArticlesView, ReviewView

router = routers.SimpleRouter(trailing_slash=False)
router.register('topics', ArticlesView)

urlpatterns = [
    path('topics/<pk>/review', ReviewView.as_view(), name='review'),
    path('', include(router.urls)),
]
