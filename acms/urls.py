"""acms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views import generic
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from acms.settings_utils import get_env_variable

admin.site.site_header = "AmaliTech"
admin.site.site_title = "AmaliTech CMS Admin Portal"
admin.site.index_title = "Welcome to AmaliTech CMS Portal"

schema_view = get_schema_view(
    openapi.Info(
        title="ACMS API Documentation",
        default_version="v1",
        description=(
            "This is a collection of all available APIs for "
            "the AmaliTech Capacity Management System"
        ),
        terms_of_service="http://localhost/",
        contact=openapi.Contact(email="cms@amalitech.com"),
        license=openapi.License(name="BSD License"),
    ),
    url=get_env_variable("DEFAULT_URL", "https://acms-api.amalitech-dev.net/"),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("", generic.RedirectView.as_view(url="/docs/", permanent=False)),
    path(
        "accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts"),
    ),
    path(
        "skills/",
        include(("skills.urls", "skills"), namespace="skills"),
    ),
    path(
        "projects/",
        include(("projects.urls", "projects"), namespace="projects"),
    )
]
