from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.organizations.models import Organization, Membership
from apps.products.models import Product


User = get_user_model()


class ProductSecurityTests(TestCase):

    def setUp(self):
        self.company_a = Organization.objects.create(
            name="ABC Electronics",
            slug="abc-electronics",
        )

        self.company_b = Organization.objects.create(
            name="XYZ Traders",
            slug="xyz-traders",
        )

        self.alice = User.objects.create_user(
            username="alice",
            password="TestPassword123!",
        )

        self.bob = User.objects.create_user(
            username="bob",
            password="TestPassword123!",
        )

        Membership.objects.create(
            organization=self.company_a,
            user=self.alice,
            role=Membership.Role.OWNER,
        )

        Membership.objects.create(
            organization=self.company_b,
            user=self.bob,
            role=Membership.Role.OWNER,
        )

        self.product_a = Product.objects.create(
            organization=self.company_a,
            name="Dell Laptop",
            sku="LAP-001",
            cost_price=Decimal("45000.00"),
            selling_price=Decimal("55000.00"),
        )

        self.product_b = Product.objects.create(
            organization=self.company_b,
            name="HP Laptop",
            sku="LAP-001",
            cost_price=Decimal("40000.00"),
            selling_price=Decimal("50000.00"),
        )

        self.client = APIClient()

    def test_owner_can_view_own_products(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.get(
            "/api/products/",
            HTTP_X_ORGANIZATION_ID=str(self.company_a.id),
        )

        self.assertEqual(response.status_code, 200)

        product_ids = [
            product["id"] for product in response.data
        ]

        self.assertIn(self.product_a.id, product_ids)
        self.assertNotIn(self.product_b.id, product_ids)

    def test_non_member_cannot_access_other_company(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.get(
            "/api/products/",
            HTTP_X_ORGANIZATION_ID=str(self.company_b.id),
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_retrieve_other_company_product(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.get(
            f"/api/products/{self.product_b.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.company_a.id),
        )

        self.assertEqual(response.status_code, 404)

    def test_owner_can_create_product(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.post(
            "/api/products/",
            {
                "name": "Wireless Mouse",
                "sku": "MOU-001",
                "cost_price": "500.00",
                "selling_price": "800.00",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.company_a.id),
        )

        self.assertEqual(response.status_code, 201)

        product = Product.objects.get(id=response.data["id"])

        self.assertEqual(
            product.organization_id,
            self.company_a.id,
        )

    def test_missing_organization_header_is_denied(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 403)
        
        
    def test_viewer_cannot_create_product(self):
        viewer = User.objects.create_user(
            username="viewer",
            password="TestPassword123!",
        )

        Membership.objects.create(
            organization=self.company_a,
            user=viewer,
            role=Membership.Role.VIEWER,
        )

        self.client.force_authenticate(user=viewer)

        response = self.client.post(
            "/api/products/",
            {
                "name": "Keyboard",
                "sku": "KEY-001",
                "cost_price": "300.00",
                "selling_price": "500.00",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.company_a.id),
        )

        self.assertEqual(response.status_code, 403)


    def test_owner_cannot_update_other_company_product(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.patch(
            f"/api/products/{self.product_b.id}/",
            {"selling_price": "999.00"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.company_a.id),
        )

        self.assertEqual(response.status_code, 404)

        self.product_b.refresh_from_db()
        self.assertEqual(
            self.product_b.selling_price,
            Decimal("50000.00"),
        )


    def test_owner_cannot_delete_other_company_product(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.delete(
            f"/api/products/{self.product_b.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.company_a.id),
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Product.objects.filter(id=self.product_b.id).exists()
        )


    def test_cannot_change_product_organization(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.patch(
            f"/api/products/{self.product_a.id}/",
            {"organization": self.company_b.id},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.company_a.id),
        )

        self.assertEqual(response.status_code, 200)

        self.product_a.refresh_from_db()
        self.assertEqual(
            self.product_a.organization_id,
            self.company_a.id,
        )    