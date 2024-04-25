from django.db import IntegrityError
from rest_framework import serializers

# from accounts.serializers import (DeveloperProfileSerializer)
from skills.models import Category, Skill, SkillRating


class CategorySerializer(serializers.ModelSerializer):

    name = serializers.CharField()

    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {"slug": {"required": False}, "name": {"required": True}}


class SkillSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Skill
        fields = "__all__"
        extra_kwargs = {
            "slug": {"required": False},
            "name": {"required": True},
        }

    def create(self, validated_data):
        """Method to create a Skill object

        Args:
            validated_data (dict): dictionary of validated data passed from
            the .validate() method

        Returns:
            Skill: an instance of the Skill object that we just created
        """
        category = validated_data.get("category")
        name = validated_data.get("name")
        try:
            skill = Skill.objects.create(category=category, name=name)
        except IntegrityError:
            error_message = f"Ths skill {name} already exists!"
            raise serializers.ValidationError(error_message)
        return skill

    def validate(self, data):
        """DRF Serializer validator to validate the request data to be
            used to create a Skill

        Args:
            data (dict): dictionary containing data

        Raises:
            serializers.ValidationError: A validation error message if the data
            is invalid

        Returns:
            dict: a dictionary of the valid data
        """
        category_slug = data.get("slug")
        try:
            category = Category.objects.get(slug=category_slug)
            del data["slug"]
            data["category"] = category
            return super().validate(data)
        except Category.DoesNotExist:
            error_message = f"Category {category_slug} does not exist!"
            raise serializers.ValidationError(error_message)


class SkillRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillRating
        fields = "__all__"
        read_only_fields = ("developer_profile",)
        extra_kwargs = {
            "comment": {"required": False},
        }


class ListSkillRatingsSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()

    class Meta:
        model = SkillRating
        fields = "__all__"
        read_only_fields = ("developer_profile", "skill")
