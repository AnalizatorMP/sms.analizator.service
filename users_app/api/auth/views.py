import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.db import IntegrityError
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from loguru import logger

from users_app.api.serializers import UserSerializer
from users_app.models import User
from utils.logger_config import log_request, api_logger


def authenticate_custom(request, email=None, password=None, **kwargs):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None

    if user.check_password(password):
        return user


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password'],
        ),
        responses={
            200: 'Успешный вход',
            401: 'Неверный логин или пароль',
        },
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate_custom(request, email=email, password=password)
        
        if user:
            if not user.is_active:
                logger.warning(f"Попытка входа неактивного пользователя: {email}")
                log_request(request, 401, f"Inactive user login attempt: {email}")
                return Response({'error': 'Email еще не подтвержден'}, status=status.HTTP_401_UNAUTHORIZED)
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            token, _ = Token.objects.get_or_create(user=user)
            
            logger.info(f"Успешный API вход пользователя: {user.email} (ID: {user.id})")
            log_request(request, 200, f"API login successful for {user.email}")
            
            return Response({'token': token.key, 'user_id': user.id})
        else:
            logger.warning(f"Неудачная попытка API входа для email: {email}")
            log_request(request, 401, f"API login failed for {email}")
            return Response({'error': 'Неверный логин или пароль'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: 'Успешный выход',
        },
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logger.info(f"API выход пользователя: {request.user.email} (ID: {request.user.id})")
        log_request(request, 200, f"API logout for {request.user.email}")
        return Response({'success': True})


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            },
            required=['email', 'password'],
        ),
        responses={
            201: 'Пользователь успешно зарегистрирован',
            400: 'Некорректные данные регистрации',
        },
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()

            logger.info(f"Новый пользователь зарегистрирован через API: {user.email} (ID: {user.id})")
            log_request(request, 201, f"API registration successful for {user.email}")

            return Response({'success': True, 'user_id': user.id}, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Ошибка валидации при API регистрации: {serializer.errors}")
        log_request(request, 400, f"API registration validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
