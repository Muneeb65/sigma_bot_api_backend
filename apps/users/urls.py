from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainSlidingView,
                                            TokenRefreshSlidingView,
                                            TokenVerifyView)

urlpatterns = [
    # ------- JWT ------- #
    path('token/', TokenObtainSlidingView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
