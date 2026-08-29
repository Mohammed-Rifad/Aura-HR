"""
URL configuration for AURA HR.

Everything public under /api/v1/ — versioning the API from the first
endpoint is far cheaper than retrofitting it once clients depend on the paths.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

api_v1 = [
    path("auth/", include("users.urls")),
    # App routes are added here as they are built:
    path("employees/", include("employees.urls")),
    path("leave/", include("leave.urls")),
    path("attendance/", include("attendance.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("org/", include("organizations.urls")),
    path("ai/", include("ai.urls")),
    path("audit/", include("audit.urls")),


]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
