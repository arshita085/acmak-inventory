from django.contrib import admin
from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "organization",
        "location",
        "is_active",
    )

    list_filter = (
        "organization",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "location",
    )