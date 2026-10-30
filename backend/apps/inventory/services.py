from django.db import transaction
from django.core.exceptions import ValidationError

from apps.organizations.models import Membership
from apps.products.models import Product
from apps.warehouses.models import Warehouse

from .models import Stock, StockMovement


@transaction.atomic
def move_stock(
    *,
    organization_id,
    product_id,
    warehouse_id,
    movement_type,
    quantity,
    user,
    reference="",
):
    # 1. Validate quantity
    if type(quantity) is not int or quantity <= 0:
        raise ValidationError(
            "Quantity must be a positive integer."
        )

    # 2. Validate movement type
    if movement_type not in (
        StockMovement.MovementType.IN,
        StockMovement.MovementType.OUT,
    ):
        raise ValidationError("Invalid movement type.")

    # 3. Check user permission
    if not user or not user.is_authenticated:
        raise ValidationError("Authentication required.")

    allowed = Membership.objects.filter(
        organization_id=organization_id,
        user=user,
        role__in=[
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
            Membership.Role.STAFF,
        ],
    ).exists()

    if not allowed:
        raise ValidationError(
            "You cannot modify this organization's stock."
        )

    # 4. Validate product and warehouse ownership
    product = Product.objects.get(
        pk=product_id,
        organization_id=organization_id,
    )

    warehouse = Warehouse.objects.get(
        pk=warehouse_id,
        organization_id=organization_id,
        is_active=True,
    )

    # 5. Ensure a stock record exists.
    # Lock the warehouse row to serialize initial stock creation.
    Warehouse.objects.select_for_update().get(pk=warehouse.pk)

    stock, _ = Stock.objects.get_or_create(
        product=product,
        warehouse=warehouse,
        defaults={"quantity": 0},
    )

    # 6. Lock the stock row before changing its balance
    stock = Stock.objects.select_for_update().get(pk=stock.pk)

    if movement_type == StockMovement.MovementType.IN:
        stock.quantity += quantity
    else:
        if stock.quantity < quantity:
            raise ValidationError(
                "Insufficient stock for this operation."
            )
        stock.quantity -= quantity

    # 7. Save stock balance
    stock.save(update_fields=["quantity", "updated_at"])

    # 8. Record movement history
    movement = StockMovement.objects.create(
        stock=stock,
        movement_type=movement_type,
        quantity=quantity,
        performed_by=user,
        reference=reference,
    )

    return movement