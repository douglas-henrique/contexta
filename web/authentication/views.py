"""
Authentication views for user management.
"""

import logging

from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import ChangePasswordSerializer, LoginSerializer, RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterView(APIView):
    """
    API endpoint for user registration.

    Allows any user to create a new account.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user and return JWT tokens."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user registered: {user.username}")

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        logger.warning(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for user login.

    Authenticates user credentials and returns JWT tokens.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)

            if user is not None:
                if not user.is_active:
                    return Response(
                        {"error": "Account is disabled."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                logger.info(f"User logged in: {user.username}")

                return Response(
                    {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            logger.warning(f"Failed login attempt for username: {username}")
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    API endpoint for user logout.

    Blacklists the refresh token to prevent further use.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist the refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"User logged out: {request.user.username}")

            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response(
                {"error": "Invalid token or token already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(APIView):
    """
    API endpoint to get current user information.

    Returns the authenticated user's data.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user data."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update current user data."""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User updated profile: {request.user.username}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    API endpoint to change user password.

    Requires authentication and validates old password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Check old password
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"error": "Old password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set new password
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            logger.info(f"User changed password: {user.username}")

            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view with logging.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.debug("Token refreshed successfully")
        return response
