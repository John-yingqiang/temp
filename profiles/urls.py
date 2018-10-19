from django.conf.urls import url
from django.urls import path, include
from .views import CreditLevelView, FeedbackView, UserConponsView, SignInView, user_redbags_view, FakeProfileView, \
    ShareFriendView, IdInfoView, ProfileView, JuPeiViewSet
from rest_framework import routers

router = routers.SimpleRouter(trailing_slash=False)
router.register('jupei', JuPeiViewSet, base_name='jupei')

urlpatterns = [
    url(r'^credit_level$', CreditLevelView.as_view(), name='credit_level'),
    url(r'^profile$', ProfileView.as_view(), name='profile'),
    url(r'^fprofile$', FakeProfileView.as_view(), name='fake_profile'),
    url(r'^feedback$', FeedbackView.as_view(), name='feedback'),
    url(r'^sign$', SignInView.as_view(), name='sign'),
    url(r'^redbags$', user_redbags_view, name='redbags'),
    url(r'^coupons$', UserConponsView.as_view(), name='coupons'),
    url(r'^shared$', ShareFriendView.as_view(), name='shared'),
    url(r'^id_info$', IdInfoView.as_view(), name='id_info'),  # 信用快手
    path('', include(router.urls)),

    ]
