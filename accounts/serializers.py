from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import DeveloperProfile, Education, User, WorkExperience
from utils.validations import validate_email, validate_password


class CurrentUserDeveloperProfileDefault:
    """Custom default class that enables the currently logged in user's
    developer profile to be used as the default value for
    the `developer_profile` field

    Raises:
        serializers.ValidationError: raised if the request object doesn't
        contain a valid user or developer profile

    Returns:
        DeveloperProfile: DeveloperProfile object
    """
    requires_context = True

    def __call__(self, serializer_field):
        request = serializer_field.context.get("request")
        if request and hasattr(request, "user"):
            return request.user.developer_profile.first()
        error_message = "The request object does not contain a valid user."
        raise serializers.ValidationError(error_message)


class EducationSerializer(serializers.ModelSerializer):
    developer_profile = serializers.HiddenField(default=CurrentUserDeveloperProfileDefault())

    class Meta:
        model = Education
        fields = "__all__"


class WorkExperienceSerializer(serializers.ModelSerializer):
    skills_used = serializers.ListField(child=serializers.CharField())
    developer_profile = serializers.HiddenField(default=CurrentUserDeveloperProfileDefault())

    class Meta:
        model = WorkExperience
        fields = "__all__"


class CountryWithCodeAndNameField(CountryField):
    """Custom Serializer class to add country name to the CountryField
    serializer

    Args:
        CountryField: django-countries default serializer class for
        the CountryField
    """
    # def to_representation(self, instance):
    #     return {
    #         "code": instance.code,
    #         "name": instance.name
    #     }


class LoginSerializer(TokenObtainPairSerializer):
    tokens = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["email", "role"]

    def validate(self, data):
        """DRF Serializer validator to validate the request data to be
            used to create a user

        Args:
            data (dict): dictionary containing request payload data

        Raises:
            serializers.ValidationError: A validation error message if the data
            is invalid

        Returns:
            dict: a dictionary of the valid data
        """
        email = data.get("email")
        USER_EXIST_MSG = f"User with email {email} already exists!"

        validate_email(email)
        user = User.objects.filter(email=email).first()
        if user is not None:
            raise serializers.ValidationError(USER_EXIST_MSG)
        return data


class AcceptInviteSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "is_active",
            "password",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
        }

    def update(self, instance, validated_data):
        """Method to update an instance of the User model

        Args:
            instance (User): the User object that is going to be updated
            validated_data (dict): A dictionary containing all the fields
            that need to be updated and have been validated with the
            self.validate() method

        Returns:
            User: an instance of the User object that we just updated
        """
        password = validated_data.pop("password")
        instance = super().update(instance, validated_data)
        instance.set_password(password)
        instance.save()

        return instance

    def validate(self, data):
        """DRF Serializer validator to validate the request data to be
            used to update a user

        Args:
            data (dict): dictionary containing request payload data

        Raises:
            serializers.ValidationError: A validation error message if the data
            is invalid

        Returns:
            dict: a dictionary of the valid data
        """
        validate_password(data.get("password"))

        return data


class UserConfigSerializer(serializers.ModelSerializer):
    profile_photo = serializers.URLField(required=False)
    country = CountryWithCodeAndNameField()

    class Meta:
        model = User
        exclude = ["password"]


class DeveloperProfileSerializer(serializers.ModelSerializer):
    user = UserConfigSerializer(read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    work_experience = WorkExperienceSerializer(many=True, read_only=True)

    class Meta:
        model = DeveloperProfile
        fields = "__all__"
