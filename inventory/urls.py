from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import MedicineViewSet, BatchViewSet, landing_page, dashboard, register

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet)
router.register(r'batches', BatchViewSet)

urlpatterns = [
    path('', landing_page, name='landing'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('api/', include(router.urls)),
]