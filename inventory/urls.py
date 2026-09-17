from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import (
    MedicineViewSet, BatchViewSet, landing_page, dashboard, register,
    ClockJobView, ImportMessyBatchesView, OutboxView
)

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet)
router.register(r'batches', BatchViewSet)

urlpatterns = [
    path('', landing_page, name='landing'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    
    # Updated Twist Endpoints using Class-Based Views
    path('clock/', ClockJobView.as_view(), name='clock'),       
    path('import/', ImportMessyBatchesView.as_view(), name='import'), 
    path('outbox/', OutboxView.as_view(), name='outbox'),        
    
    path('api/', include(router.urls)),
]