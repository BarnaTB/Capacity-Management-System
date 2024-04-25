from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import DeveloperProfile
from skills.models import Category, Skill, SkillRating
from skills.serializers import (CategorySerializer, ListSkillRatingsSerializer,
                                SkillRatingSerializer, SkillSerializer)
from utils.permissions import IsAdmin, IsDeveloper, IsProjectManager


class ListCreateCategoryAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None


class ListCreateSkillAPIView(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated & IsAdmin | IsDeveloper | IsProjectManager]
    pagination_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()


class SkillDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Skill.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, *args, **kwargs):
        """APIView to delete all skills"""
        number_deleted_int, number_deleted_dict = self.get_queryset().delete()

        response_data = {
            "data": None,
            "message": f"Deleted {number_deleted_int} skills successfully.",
            "status": "success",
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class AdminRetrieveUpdateDestroyMixin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated & IsAdmin]


class CategoryUpdateDestroyAPIView(AdminRetrieveUpdateDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SkillUpdateDestroyAPIView(AdminRetrieveUpdateDestroyMixin):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class SkillRatingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SkillRatingSerializer
    permission_classes = [IsAuthenticated & IsDeveloper]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        user = self.request.user
        developer_profile = user.developer_profile.first()
        queryset = SkillRating.objects.filter(developer_profile=developer_profile)

        serializer = ListSkillRatingsSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = self.request.user
        developer_profile = DeveloperProfile.objects.get(user=user)

        skill_rating = serializer.save(developer_profile=developer_profile)

        return skill_rating
