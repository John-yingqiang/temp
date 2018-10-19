
from django.urls import path
from django.conf.urls import url, include
from django.contrib import admin
from common.views import live_check
from .settings import DEBUG
from rest_framework import routers
from django.conf.urls import url, include
from stores.views import CouponsView


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'stores', CouponsView, 'stores')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('live_check/<str:p>', live_check),
    path('misc/infos/', include('api_infos.urls')),
    path('misc/profiles/', include('profiles.urls')),
    path('misc/stores/', include('stores.urls')),
    path('misc/collects/', include('collects.urls')),
    path('misc/', include('topics.urls')),
    path('misc/', include(router.urls)),
    path('api/base/', include('tasks.urls')),
]


if DEBUG:
    import debug_toolbar
    urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
    ]
