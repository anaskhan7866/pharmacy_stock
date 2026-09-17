from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, BatchViewSet

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet)
router.register(r'batches', BatchViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]