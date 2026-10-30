from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.organizations.models import Organization, Membership
from apps.products.models import Product
from apps.warehouses.models import Warehouse
from apps.inventory.models import Stock, StockMovement
from apps.inventory.services import move_stock
from unittest.mock import patch

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

    def test_stock_out_prevents_insufficient_stock(self):
        # Receive 10 units
        move_stock(
            organization_id=self.org.id,
            product_id=self.product.id,
            warehouse_id=self.warehouse.id,
            movement_type=StockMovement.MovementType.IN,
            quantity=10,
            user=self.user,
        )

        # Attempt to dispatch 20 units
        with self.assertRaises(ValidationError):
            move_stock(
                organization_id=self.org.id,
                product_id=self.product.id,
                warehouse_id=self.warehouse.id,
                movement_type=StockMovement.MovementType.OUT,
                quantity=20,
                user=self.user,
            )

        # Verify stock was not reduced
        stock = Stock.objects.get(
            product=self.product,
            warehouse=self.warehouse,
        )

        self.assertEqual(stock.quantity, 10)

        # Only one successful movement exists
        self.assertEqual(
            StockMovement.objects.filter(stock=stock).count(),
            1,
        )
        

    def test_user_cannot_modify_another_organization_stock(self):
    # Create a second organization
        other_org = Organization.objects.create(
            name="Other Electronics",
            slug="other-electronics",
        )

        # Create a product belonging to the second organization
        other_product = Product.objects.create(
            organization=other_org,
            name="Other Laptop",
            sku="OTHER-LAP-001",
            cost_price="30000.00",
            selling_price="40000.00",
        )

        # Create a warehouse belonging to the second organization
        other_warehouse = Warehouse.objects.create(
            organization=other_org,
            name="Other Warehouse",
            code="OTHER-WH-001",
        )

        # Our user belongs only to self.org, not other_org
        with self.assertRaises(ValidationError):
            move_stock(
                organization_id=other_org.id,
                product_id=other_product.id,
                warehouse_id=other_warehouse.id,
                movement_type=StockMovement.MovementType.IN,
                quantity=10,
                user=self.user,
            )

        # Confirm no stock or movement was created
        self.assertFalse(
            Stock.objects.filter(
                product=other_product,
                warehouse=other_warehouse,
            ).exists()
        )

        self.assertFalse(
            StockMovement.objects.filter(
                stock__product=other_product,
                stock__warehouse=other_warehouse,
            ).exists()
        )
        
        
    def test_stock_transaction_rollback(self):
    # First, receive 10 units successfully
        move_stock(
            organization_id=self.org.id,
            product_id=self.product.id,
            warehouse_id=self.warehouse.id,
            movement_type=StockMovement.MovementType.IN,
            quantity=10,
            user=self.user,
        )

        stock = Stock.objects.get(
            product=self.product,
            warehouse=self.warehouse,
        )

        # Simulate a failure while saving movement history
        with patch.object(
            StockMovement.objects,
            "create",
            side_effect=RuntimeError("Movement save failed"),
        ):
            with self.assertRaises(RuntimeError):
                move_stock(
                    organization_id=self.org.id,
                    product_id=self.product.id,
                    warehouse_id=self.warehouse.id,
                    movement_type=StockMovement.MovementType.OUT,
                    quantity=5,
                    user=self.user,
                )

        # Reload from database
        stock.refresh_from_db()

        # The original 10 units must remain
        self.assertEqual(stock.quantity, 10)

        # Only the successful IN movement should exist
        self.assertEqual(
            StockMovement.objects.filter(stock=stock).count(),
            1,
        )