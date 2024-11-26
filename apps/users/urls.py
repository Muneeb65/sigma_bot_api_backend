from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainSlidingView,
                                            TokenRefreshSlidingView,
                                            TokenVerifyView, )
from .views import (UserViewSet,
                    RequestPasswordResetViewSet,
                    VerifyPasswordResetTokenViewSet,
                    SetNewPasswordViewSet,
                    VerifyEmailViewSet)

urlpatterns = [
    # ------- JWT ------- #
    path('token/', TokenObtainSlidingView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('register/', UserViewSet.as_view(), name='signup'),
    path('verify-email/', VerifyEmailViewSet.as_view(), name='verify-email'),
    path('forgot-password/', RequestPasswordResetViewSet.as_view(), name='forgot-password'),
    path('verify-password-token/', VerifyPasswordResetTokenViewSet.as_view(), name='verify-password-token'),
    path('reset-password/', SetNewPasswordViewSet.as_view(), name='reset-password'),
]
