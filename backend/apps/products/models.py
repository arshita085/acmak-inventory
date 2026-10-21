from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    organization = models.ForeignKey(
    "organizations.Organization",
    on_delete=models.PROTECT,
    related_name="products",
)

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "sku"],
                name="unique_product_sku_per_organization",
            )
    ]

    def __str__(self):
        return f"{self.name} ({self.sku})"