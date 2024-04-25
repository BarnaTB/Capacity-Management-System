from django.urls import path

from accounts.views import (AcceptInviteAPIView, DeveloperProfileAPIView,
                            DeveloperProfileListAPIView,
                            DeveloperProfileUpdateView, DeveloperProfileView,
                            EducationDetailView, LoginAPIView,
                            SendInvitationView, UpdateUserAPIView,
                            UserConfigView, UserListView,
                            WorkExperienceDetailView)

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("send-invite/", SendInvitationView.as_view(), name="Send invitation"),
    path(
        "accept-invite/<str:uid>/<str:token>/",
        AcceptInviteAPIView.as_view(),
        name="user-retrieve-update",
    ),
    path("user/", UserConfigView.as_view(), name="user"),
    path("update-user/", UpdateUserAPIView.as_view(), name="user"),
    path("users/", UserListView.as_view(), name="user-list"),
    path('developer-profiles/', DeveloperProfileListAPIView.as_view()),
    path('developer-profile/', DeveloperProfileAPIView.as_view(), name="developer-profile"),
    path("developer/<int:id>", DeveloperProfileView.as_view(), name="view-developer profile"),
    path("developer-profile/update/", DeveloperProfileUpdateView.as_view(), name="developer-profile-update"),
    path("work-experience/<int:pk>", WorkExperienceDetailView.as_view(), name="work-experience-retrieve-update-delete"),
    path("education/<int:pk>", EducationDetailView.as_view(), name="education-retrieve-update-delete"),
]
