from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import DeveloperProfile
from projects.models import Project
from projects.serializers import AssignProjectSerializer, ProjectSerializer
from projects.utils import get_suggested_profiles
from utils.decorators import required_fields
from utils.exceptions import CustomAPIException
from utils.permissions import IsAdmin, IsDeveloper, IsProjectManager
from utils.send_email import send_project_assignment_email


class CreateProjectView(CreateAPIView):
    permission_classes = [IsAuthenticated & IsAdmin | IsProjectManager]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    @required_fields(
        ["name", "description", "start_date", "end_date", "required_skills"]
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except Exception as e:
            raise CustomAPIException(message=str(e))

    def perform_create(self, serializer):
        project = serializer.save()
        project.created_by = self.request.user
        project.save()


class ListProjectsDetailView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()


class RetreiveProjectDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"


class AssignProjectToDeveloperView(UpdateAPIView):
    permission_classes = [IsAuthenticated & IsAdmin | IsProjectManager]
    serializer_class = AssignProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"

    def patch(self, request, *args, **kwargs):
        project = self.get_object()
        member_ids = request.data.get("members", [])
        developers = DeveloperProfile.objects.filter(id__in=member_ids)
        if len(developers) != len(member_ids):
            return CustomAPIException(message="One or more developer profiles is invalid!", status=status.HTTP_400_BAD_REQUEST)
        project.members.add(*developers)

        for developer in developers:
            send_project_assignment_email(developer, project)

        developers.update(availability=False, current_project_start_date=project.start_date, current_project_end_date=project.end_date, current_project=project.name)
        serializer = self.get_serializer(project)
        return Response(serializer.data)


class UpdateProjectView(UpdateAPIView):
    permission_classes = [IsAuthenticated & (IsAdmin | IsProjectManager)]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"


class DestroyProjectView(DestroyAPIView):
    permission_classes = [IsAuthenticated & IsAdmin | IsProjectManager]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"


class DeveloperProjectsListView(ListAPIView):
    permission_classes = [IsAuthenticated & (IsDeveloper | IsAdmin | IsProjectManager)]
    serializer_class = ProjectSerializer
    # User = User()

    def get_queryset(self):
        user_id = self.kwargs['id']

        developer = get_object_or_404(DeveloperProfile, user__id=user_id)
        projects = Project.objects.filter(members__id=developer.id).distinct().order_by('-create_date')

        return projects


class SuggestedDevelopersListView(ListAPIView):
    """List API View that enables users to retrieve a list of
    suggested developers to be assigned to a project based on the project's
    required skills and the developer's skills
    """

    def get_queryset(self):
        project_slug = self.kwargs["slug"]
        project = Project.objects.get(slug=project_slug)
        required_skills = project.required_skills.all()
        developer_profiles = DeveloperProfile.objects.filter(
            Q(skills__in=required_skills) & Q(availability=True) | Q(current_project_end_date__lt=project.start_date)
        ).distinct()

        return developer_profiles

    def list(self, request, *args, **kwargs):
        developer_profiles = self.get_queryset()
        project_slug = self.kwargs.get("slug")
        project = Project.objects.get(slug=project_slug)
        suggested_profiles = get_suggested_profiles(project, developer_profiles)

        if not suggested_profiles:
            error_message = """Considering the project's start_date, there are
            currently no available developers with the matching skillset for
            this project's requirements but you can still peruse the list of
            developers and assign any you deem fit."""
            raise CustomAPIException(message=error_message)

        return Response(suggested_profiles)
