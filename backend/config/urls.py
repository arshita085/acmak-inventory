from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({
        "status": "success",
        "application": "ACMAK Inventory",
        "message": "Backend API is running successfully",
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
    path("api/products/", include("apps.products.urls")),
    path("api-auth/", include("rest_framework.urls")),
]