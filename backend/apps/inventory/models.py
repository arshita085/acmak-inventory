from django.db import models
from django.db.models import Q, F


class Stock(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="stock_records",
    )

    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="stock_records",
    )

    quantity = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "warehouse"],
                name="unique_stock_per_product_warehouse",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=0),
                name="stock_quantity_non_negative",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.warehouse.name}: "
            f"{self.quantity}"
        )
        
        
from django.conf import settings


class StockMovement(models.Model):

    class MovementType(models.TextChoices):
        IN = "IN", "Stock In"
        OUT = "OUT", "Stock Out"

    stock = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT,
        related_name="movements",
    )

    movement_type = models.CharField(
        max_length=3,
        choices=MovementType.choices,
    )

    quantity = models.PositiveIntegerField()

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="stock_movement_positive_quantity",
            ),
        ]

    def __str__(self):
        return (
            f"{self.movement_type} - "
            f"{self.stock.product.name} - "
            f"{self.quantity}"
        )        