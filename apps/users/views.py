import logging

from django.db.models import Count, F, Prefetch, Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import (UserSerializer, VerifyEmailSerializer,
                          RequestPasswordResetSerializer, VerifyPasswordResetTokenSerializer,
                          SetNewPasswordSerializer)

from .utils import send_verification_email

logger = logging.getLogger('django')


class UserViewSet(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user)

        headers = self.get_success_headers(serializer.data)
        data = {'message': ('A verification email has been sent to you please verify'
                            ' your email to confirm registration.')}
        return Response(data, status=status.HTTP_201_CREATED, headers=None)


class VerifyEmailViewSet(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            response = Response(data=serializer.validated_data)
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response


# class LoginViewSet(ObtainJSONWebToken):
#     permission_classes = [AllowAny]
#     serializer_class = LoginSerializer
#     throttle_classes = [LoginThrottler]


# class ResendCodeViewSet(ObtainJSONWebToken):
#     permission_classes = [AllowAny]
#     serializer_class = ResendCodeSerializer
#     throttle_classes = [LoginThrottler]


# class ObtainJWTViewSet(ObtainJSONWebToken):
#     permission_classes = [AllowAny]
#     serializer_class = ObtainJWTSerializer
#     throttle_classes = [ObtainJWTThrottler]


class RequestPasswordResetViewSet(APIView):
    permission_classes = [AllowAny]
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, context={'user': self.request.user})
            if serializer.is_valid():
                self.send_password_reset_email(serializer.validated_data)
        except:
            pass
        # Sending same message to avoid email enumeration
        return Response({'message': ('If the email exists, an email will be sent with further instructions.')})

    def send_password_reset_email(self, validated_data):
        subject_template = "emails/password_reset_subject.txt"
        body_template = "emails/password_reset_email.html"
        to = [validated_data.get('user').email]

        Mailer.send_email_with_template(
            subject_template=subject_template,
            body_template=body_template,
            context=validated_data,
            to=to
        )


class VerifyPasswordResetTokenViewSet(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyPasswordResetTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            response = Response(data=serializer.validated_data)
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response


class SetNewPasswordViewSet(APIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            response = Response(data=serializer.validated_data)
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response


