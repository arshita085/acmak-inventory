from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "sku",
        "cost_price",
        "selling_price",
        "is_active",
        "created_at",
    )

    search_fields = ("name", "sku")
    list_filter = ("is_active",)