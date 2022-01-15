from django.urls import path, re_path
from . import views
from rest_framework import routers

# from rest_framework_simplejwt.views import (
#     TokenRefreshView,
# )
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path(
        "profile/<user__id>/",
        views.UserProfileSerializerView.as_view(),
        name="user_profile",
    ),
    path(
        "myplan/<user__id>/",
        views.UserPlanSerializerView.as_view(),
        name="myplan",
    ),
    path("test_payment/", views.test_payment, name="test_payment"),
    path("token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("signup/", views.UserCreateSerializerView.as_view(), name="user__signup"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("plans/", views.PlansView.as_view(), name="plans"),
]
