from rest_framework import filters
from .models import CouponType
from django.db.models import Q
from .serializers import CouponTypeSerializer, CouponFilterSerializer


# 热门
class IsHotFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        serializer = CouponFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        is_hot = params.get('is_hot')
        is_birthday = params.get('is_birthday')
        is_new_register = params.get('is_new_register')
        if is_hot:
            queryset = queryset.filter(is_hot=True)
        if is_birthday:
            queryset = queryset.filter(is_birthday=True)
        if is_new_register:
            queryset = queryset.filter(is_new_register=True)

        return queryset