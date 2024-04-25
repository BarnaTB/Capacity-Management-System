from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import DeveloperProfile, Education, User, WorkExperience
from accounts.serializers import (AcceptInviteSerializer,
                                  DeveloperProfileSerializer,
                                  EducationSerializer, LoginSerializer,
                                  UserConfigSerializer, UserSerializer,
                                  WorkExperienceSerializer)
from accounts.utils import validate_user_by_uid
from acms.settings_utils import get_env_variable
from skills.models import SkillRating
from skills.serializers import ListSkillRatingsSerializer
from utils.auth import TokenGenerator
from utils.decorators import required_fields
from utils.exceptions import CustomAPIException
from utils.general import upload_to_s3
from utils.permissions import (IsAdmin, IsDeveloper, IsNotAuthenticated,
                               IsProjectManager)
from utils.send_email import send_email


class LoginAPIView(TokenObtainPairView):
    """
    Login API. Expects an email and password

    :returns: access and refresh token
    """

    permission_classes = [IsNotAuthenticated]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SendInvitationView(generics.GenericAPIView):
    """APIView to enable an ADMIN user to send an invitation to
    other users to join the system

    Returns:
        Response: a Response data object that contains a success message
        if the invitation email is sent successfully and an error message
        if it's not
    """

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer

    def post(self, request):
        FAIL_STATUS = "Fail"
        SUCCESS_MSG = "Email sent successfully"
        FRONTEND_DOMAIN_NAME = get_env_variable("FRONTEND_DOMAIN_NAME", "")
        FAIL_TO_SEND_MESSAGE = "Fail to send email!"
        response_data = {"message": SUCCESS_MSG, "status": FAIL_STATUS, "data": None}

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        encoded_uid = urlsafe_base64_encode(force_bytes(user.id))
        token_generator = TokenGenerator()
        token = token_generator.make_token(user)

        link = f"{FRONTEND_DOMAIN_NAME}/accept-invite/{token}/{encoded_uid}"
        subject = "Invitation to Join ACMS"
        expiry_time_hours = settings.TOKEN_EXPIRED_AFTER_SECONDS / 3600
        data = {"link": link, "expiry_time": expiry_time_hours}
        message = render_to_string("email_invitation.html", data)

        send = send_email(subject, message, user.email)
        if not send:
            user.delete()
            raise CustomAPIException(message=FAIL_TO_SEND_MESSAGE)
        response_data["data"] = serializer.data
        response_data["status"] = "success"
        return Response(response_data, status=status.HTTP_200_OK)


class AcceptInviteAPIView(generics.RetrieveUpdateAPIView):
    """API view class to enable a user to accept an invite.
    Expects a valid token, first and last name, email, password
    and confirm password fields

    :returns: user credentials for the newly activated user account
    """

    permission_classes = [
        AllowAny,
    ]
    serializer_class = AcceptInviteSerializer
    queryset = User.objects.all()

    @required_fields(["uid", "token"])
    def update(self, request, *args, **kwargs):
        """Method to update the user's detail and activate their account"""
        uid = kwargs.get("uid")
        token = kwargs.get("token")
        error_message = "Invalid activation link!"
        user = validate_user_by_uid(uid)

        if not user:
            raise CustomAPIException(message=error_message)
        if user.is_active:
            error_message = "Your account is already active. Proceed to login!"
            raise CustomAPIException(message=error_message)

        token_generator = TokenGenerator()

        if not token_generator.check_token(user, token):
            raise CustomAPIException(message=error_message)

        data = request.data
        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        user.is_active = True
        user.save()
        serializer.save()

        response_data = {
            "message": "Account activated successfully!",
            "user": serializer.data,
            "tokens": user.tokens,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserConfigView(generics.RetrieveAPIView):
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return get_object_or_404(User, pk=user.pk)


class UpdateUserAPIView(generics.UpdateAPIView):
    """API view class to enable a user to update their details.
    Expects any field that the user wishes to update

    :returns: a dictionary containing the updated data and any other user
    information
    """
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(get_user_model(), email=self.request.user.email)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(user, data=request.data, partial=True)

        profile_photo = request.FILES.get("profile_photo")

        if profile_photo:
            photo_url = upload_to_s3(profile_photo)
            if not photo_url:
                error_message = "There was an error uploading your photo!"
                raise CustomAPIException(message=error_message)
            serializer.initial_data["profile_photo"] = photo_url

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """APIView to enable logged in users to view users based on their role
    """
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated & (IsAdmin | IsProjectManager)]

    def get_queryset(self):
        user = self.request.user
        return user.get_users_by_role()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class DeveloperProfileListAPIView(generics.ListAPIView):
    """APIView to list developer profiles based on availability
    """
    serializer_class = DeveloperProfileSerializer
    permission_classes = [IsAuthenticated & (IsAdmin | IsProjectManager)]

    def get_queryset(self):
        queryset = DeveloperProfile.objects.all()
        availability = self.request.query_params.get("availability")
        if availability is not None:
            queryset = queryset.filter(availability=availability)
        return queryset


class DeveloperProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated & (IsAdmin | IsProjectManager)]
    serializer_class = DeveloperProfileSerializer
    queryset = DeveloperProfile.objects.all()
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        developer_profile = self.get_object()
        serializer = self.get_serializer(developer_profile)
        skill_ratings = SkillRating.objects.filter(developer_profile=developer_profile)
        serialized_skill_ratings = ListSkillRatingsSerializer(skill_ratings, many=True)
        serializer.data["skill_ratings"] = serialized_skill_ratings
        response_data = {
            "skill_ratings": serialized_skill_ratings.data,
            "developer_profile": serializer.data
        }
        return Response(response_data)


class DeveloperProfileUpdateView(generics.UpdateAPIView):
    """APIView to enable developers to update their developer profile with
    work experience and education background
    """
    serializer_class = DeveloperProfileSerializer
    permission_classes = [IsAuthenticated & IsDeveloper]

    def get_object(self):
        return self.request.user.developer_profile.first()

    def patch(self, request, *args, **kwargs):
        developer_profile = self.get_object()
        data = request.data
        work_experience_data = data.get("work_experience")
        education_data = data.get("education")

        if work_experience_data:
            work_experience_serializer = WorkExperienceSerializer(data=work_experience_data, context={"request": request}, many=True, partial=True)
            work_experience_serializer.is_valid(raise_exception=True)
            work_experience_serializer.save(developer_profile=developer_profile)
        if education_data:
            education_serializer = EducationSerializer(data=education_data, context={"request": request}, many=True, partial=True)
            education_serializer.is_valid(raise_exception=True)
            education_serializer.save(developer_profile=developer_profile)

        employment_status = data.get("employment_status")
        job_information = data.get("job_information")

        if employment_status or job_information:
            developer_profile.employment_status = employment_status
            developer_profile.job_information = job_information
            developer_profile.save()
        profile_serializer = self.get_serializer(developer_profile, partial=True)

        return Response(profile_serializer.data, status=status.HTTP_200_OK)


class WorkExperienceEducationMixin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated & IsDeveloper]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs.get("pk"))
        return obj


class WorkExperienceDetailView(WorkExperienceEducationMixin):
    """API View to enable a developer to retrieve, update or delete
    a single work experience entry
    """
    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        user = self.request.user
        developer_profile = user.developer_profile.first()
        return WorkExperience.objects.filter(developer_profile=developer_profile)


class EducationDetailView(WorkExperienceEducationMixin):
    """API View to enable a developer to retrieve, update or delete
    a single education entry
    """
    serializer_class = EducationSerializer

    def get_queryset(self):
        user = self.request.user
        developer_profile = user.developer_profile.first()
        return Education.objects.filter(developer_profile=developer_profile)


class DeveloperProfileAPIView(generics.RetrieveAPIView):
    """API View to enable a logged in developer to view their developer profile
    """
    serializer_class = DeveloperProfileSerializer
    permission_classes = [IsAuthenticated & IsDeveloper]

    def get_object(self):
        return self.request.user.developer_profile.first()
