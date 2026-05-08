

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
from weasyprint import HTML
from django.conf import settings

from .models import Supplier, PurchaseOrder, CompanyProfile
from .serializers import SupplierSerializer, PurchaseOrderSerializer


# ------------------------------------
# SUPPLIER VIEWSET (API)
# ------------------------------------
class SupplierViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating, listing, and updating suppliers.
    """
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer


# ------------------------------------
# PURCHASE ORDER VIEWSET (API)
# ------------------------------------
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing purchase orders and generating PDFs.
    """
    queryset = PurchaseOrder.objects.prefetch_related("items").select_related("supplier").all()
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ["supplier__name", "date"]

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        """
        Generate a purchase order PDF via API (requires authentication).
        Example: /api/purchase-orders/<id>/pdf/
        """
        purchase_order = self.get_object()
        company = CompanyProfile.objects.first()

        if not company:
            return Response(
                {"error": "Company profile not configured."},
                status=500
            )

        # Render HTML template
        html_content = render_to_string(
            "purchase_orders/purchase_order_pdf.html",
            {"purchase_order": purchase_order, "company": company},
        )


        pdf = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()


        # Filename and response
        filename = f"{purchase_order.po_number or 'purchase_order'}.pdf"
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response


# ------------------------------------
# ADMIN-SAFE PDF VIEW (NO AUTH TOKEN)
# ------------------------------------
@staff_member_required
def purchase_order_pdf_admin_view(request, pk):
    """
    Admin-only version of PDF generator — no DRF authentication required.
    Used by the 'Print Purchase Order' button in Django Admin.
    Example: /admin/purchase-orders/<id>/print/
    """

    try:
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    except Http404:
        return HttpResponse("Purchase order not found. SOMETHING ", status=404)
    
    company = CompanyProfile.objects.first()
    if not company:
        return HttpResponse("Company profile not configured.", status=500)

    # Render HTML for PDF
    html = render_to_string(
        "purchase_order/purchase_order_pdf.html",
        {"purchase_order": purchase_order, "company": company},
    )

    # Generate the PDF
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    filename = f"{purchase_order.po_number or 'purchase_order'}.pdf"

    # Return PDF in browser
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
