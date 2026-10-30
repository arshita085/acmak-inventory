from django.contrib import admin
from .models import Stock, StockMovement


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "warehouse",
        "quantity",
        "updated_at",
    )

    list_filter = ("warehouse",)

    search_fields = (
        "product__name",
        "product__sku",
        "warehouse__name",
    )

    readonly_fields = (
        "product",
        "warehouse",
        "quantity",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "stock",
        "movement_type",
        "quantity",
        "performed_by",
        "reference",
        "created_at",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    search_fields = (
        "stock__product__name",
        "stock__product__sku",
        "reference",
    )

    readonly_fields = (
        "stock",
        "movement_type",
        "quantity",
        "performed_by",
        "reference",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False    