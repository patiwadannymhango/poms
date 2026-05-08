
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from rest_framework import routers
# from purchase_order.views import SupplierViewSet, PurchaseOrderViewSet, purchase_order_pdf_admin_view

# router = routers.DefaultRouter()
# router.register(r"purchase-orders", PurchaseOrderViewSet)
# router.register(r"suppliers", SupplierViewSet)

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("api/", include(router.urls)),
#     path("admin/purchase_orders/<int:pk>/print/", purchase_order_pdf_admin_view, name="purchase-order-pdf-admin"),
# ]


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from purchase_order.views import (
    SupplierViewSet,
    PurchaseOrderViewSet,
    purchase_order_pdf_admin_view,
)

router = routers.DefaultRouter()
router.register(r"purchase-orders", PurchaseOrderViewSet)
router.register(r"suppliers", SupplierViewSet)

urlpatterns = [
    # Custom admin print URL FIRST
    path(
        "admin/purchase_order/<int:pk>/print/",
        purchase_order_pdf_admin_view,
        name="purchase-order-pdf-admin",
    ),

    # Django Admin
    path("admin/", admin.site.urls),

    # API Routes
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )