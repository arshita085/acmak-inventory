from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.organizations.models import Organization, Membership
from apps.products.models import Product
from apps.warehouses.models import Warehouse
from apps.inventory.models import Stock, StockMovement
from apps.inventory.services import move_stock


class StockServiceTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="stocktester",
            password="TestPassword123!",
        )

        self.org = Organization.objects.create(
            name="Test Electronics",
            slug="test-electronics",
        )

        Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.Role.OWNER,
        )

        self.product = Product.objects.create(
            organization=self.org,
            name="Test Laptop",
            sku="TEST-LAP-001",
            cost_price="40000.00",
            selling_price="50000.00",
        )

        self.warehouse = Warehouse.objects.create(
            organization=self.org,
            name="Main Warehouse",
            code="WH-TEST-001",
        )

    def test_stock_in_increases_quantity(self):
        move_stock(
            organization_id=self.org.id,
            product_id=self.product.id,
            warehouse_id=self.warehouse.id,
            movement_type=StockMovement.MovementType.IN,
            quantity=20,
            user=self.user,
            reference="TEST-IN-001",
        )

        stock = Stock.objects.get(
            product=self.product,
            warehouse=self.warehouse,
        )

        self.assertEqual(stock.quantity, 20)

        self.assertEqual(
            StockMovement.objects.filter(stock=stock).count(),
            1,
        )