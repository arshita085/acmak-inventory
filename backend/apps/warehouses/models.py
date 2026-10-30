from django.db import models


class Warehouse(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="warehouses",
    )

    name = models.CharField(max_length=200)

    code = models.CharField(max_length=30)

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_warehouse_code_per_org",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"