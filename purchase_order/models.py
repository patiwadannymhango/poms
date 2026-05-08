from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, F


class CompanyProfile(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("16.00"))

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
    
    
class ShipTo(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

# Quotation number generator (per-year sequence)
class PurchaseOrderSequence(models.Model):
    year = models.IntegerField(unique=True)
    seq = models.PositiveIntegerField(default=0)


class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="quotations")
    ship_to = models.ForeignKey(ShipTo, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    po_number = models.CharField(max_length=225, unique=True, blank=True)
    payment_terms = models.CharField(max_length=255, default="20 days")
    date_required = models.DateField(null=True, blank=True)
    shipping_method = models.CharField(max_length=255, blank=True)
    shipping_terms = models.CharField(max_length=255, blank=True)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=255, blank=True)
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("16.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.po_number or f"Purchase Order {self.pk}"

    # Auto-generate purchase order number
    @staticmethod
    def _generate_po_number():
        today = timezone.now().date()
        year = today.year
        with transaction.atomic():
            seq_obj, _ = PurchaseOrderSequence.objects.select_for_update().get_or_create(year=year)
            seq_obj.seq += 1
            seq_obj.save()
            # return f"PO {year}{seq_obj.seq:04d}"
            return f"PO-{year}-{seq_obj.seq:04d}"

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self._generate_po_number()
        super().save(*args, **kwargs)

    # ---- Safe Financial Properties ----
    @property
    def subtotal(self):
        agg = self.items.aggregate(
            total=Sum(F("quantity") * F("unit_price"), output_field=models.DecimalField())
        )
        total = agg["total"]
        if total is None:
            return Decimal("0.00")
        return Decimal(total).quantize(Decimal("0.01"))

    @property
    def vat_amount(self):
        return (self.subtotal * (self.vat_percent / Decimal("100"))).quantize(Decimal("0.01"))

    @property
    def total(self):
        return (self.subtotal + self.vat_amount).quantize(Decimal("0.01"))


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    description = models.TextField()
    uom = models.CharField(max_length=50, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.description[:30]}..."

    @property
    def line_total(self):
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))
