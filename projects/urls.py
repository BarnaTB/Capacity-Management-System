from django.urls import path

from projects.views import (AssignProjectToDeveloperView, CreateProjectView,
                            DestroyProjectView, DeveloperProjectsListView,
                            ListProjectsDetailView, RetreiveProjectDetailView,
                            SuggestedDevelopersListView, UpdateProjectView)

urlpatterns = [
    path("", ListProjectsDetailView.as_view(), name="project-list"),
    path("create/", CreateProjectView.as_view(), name="project-create"),
    path("<str:slug>/", RetreiveProjectDetailView.as_view(), name="project-detail"),
    path("<str:slug>/update/", UpdateProjectView.as_view(), name="project-update"),
    path("<str:slug>/delete/", DestroyProjectView.as_view(), name="project-delete"),
    path("<str:slug>/assign/", AssignProjectToDeveloperView.as_view(), name="project-assign-to-developer"),
    path("<int:id>/developer/", DeveloperProjectsListView.as_view(), name="view-developer-projects"),
    path("<str:slug>/suggested-developers/", SuggestedDevelopersListView.as_view(), name="suggested-developers-list"),
]
