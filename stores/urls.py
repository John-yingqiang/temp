from django.conf.urls import url
from .views import CouponHomeView, coins_home_view, EarnCoinView


urlpatterns = [
    url(r'^earn$', EarnCoinView.as_view(), name='earn'),
    url(r'^home$', CouponHomeView.as_view(), name='coupon_home'),
    url(r'^coins$', coins_home_view, name='coins_home'),
    ]
