from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Product
from .serializers import ProductSerializer
from .permissions import ProductPermission


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]

    def get_organization_id(self):
        org_id = self.request.headers.get("X-Organization-ID")

        if not org_id or not org_id.isdecimal():
            raise ValidationError({
                "organization": "A valid X-Organization-ID header is required."
            })

        return int(org_id)

    def get_queryset(self):
        return Product.objects.filter(
            organization_id=self.get_organization_id()
        )

    def perform_create(self, serializer):
        serializer.save(
            organization_id=self.get_organization_id()
        )