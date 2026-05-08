from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, CompanyProfile

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = PurchaseOrderItem
        fields = ("id","description","uom","quantity","unit_price","line_total")

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    vat_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ("id","po_number","supplier","date","delivery_date","payment_terms",
                  "authorizer_name","vat_percent","items","subtotal","vat_amount","total")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for item in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item)
        return purchase_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", [])
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        # replace items (simple approach)
        instance.items.all().delete()
        for item in items_data:
            PurchaseOrderItem.objects.create(purchase_order=instance, **item)
        return instance

