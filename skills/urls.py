from django.urls import path

from skills.views import (CategoryUpdateDestroyAPIView,
                          ListCreateCategoryAPIView, ListCreateSkillAPIView,
                          SkillDeleteAllAPIView, SkillRatingListCreateAPIView,
                          SkillUpdateDestroyAPIView)

urlpatterns = [
    path(
        "categories/",
        ListCreateCategoryAPIView.as_view(),
        name="list-create-categories",
    ),
    path(
        "categories/<str:pk>",
        CategoryUpdateDestroyAPIView.as_view(),
        name="retrieve-update-delete-category",
    ),
    path("skills/", ListCreateSkillAPIView.as_view(), name="list-create-skills"),
    path(
        "skills/delete-all/", SkillDeleteAllAPIView.as_view(), name="delete-all-skills"
    ),
    path(
        "skills/<str:pk>",
        SkillUpdateDestroyAPIView.as_view(),
        name="retrieve-update-delete-skill",
    ),
    path(
        "add-to-profile/",
        SkillRatingListCreateAPIView.as_view(),
        name="skillrating-list",
    ),
]
