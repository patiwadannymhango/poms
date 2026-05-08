

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import PurchaseOrder, PurchaseOrderItem, CompanyProfile, PurchaseOrderSequence, ShipTo, Supplier


admin.site.site_header = "Tripple K Engineering Admin"
admin.site.site_title = "Tripple K Admin Portal"
admin.site.index_title = "Welcome to Tripple K System"


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem 
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    exclude = ("po_number",)
    list_display = ("po_number", "supplier", "date", "total", "print_button")
    readonly_fields = ("po_number", "print_button")
    inlines = [PurchaseOrderItemInline]


    def print_button(self, obj):
        if not obj.pk:
            return "-"
        # ✅ New path (no admin/ prefix)
        url = reverse("purchase-order-pdf-admin", args=[obj.pk])

        return format_html(
            '<a href="{}" target="_blank" '
            'style="padding:10px 20px; font-size:12px; background:#2b7de9; '
            'color:white; border-radius:3px; text-decoration:none;">🖨 Print</a>',
            url,
        )

    print_button.short_description = "Print Purchase Order"


@admin.register(Supplier)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")


@admin.register(ShipTo)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")


admin.site.register(PurchaseOrderSequence)
