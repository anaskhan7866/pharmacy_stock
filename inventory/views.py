import re
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Medicine, Batch, Notification
from .serializers import MedicineSerializer, BatchSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']

    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        medicine = self.get_object()
        try:
            requested_quantity = int(request.data.get('quantity', 0))
        except ValueError:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        if requested_quantity <= 0:
            return Response({'error': 'Quantity > 0 required'}, status=status.HTTP_400_BAD_REQUEST)

        if medicine.total_sellable_stock() < requested_quantity:
            return Response({'error': 'Insufficient valid stock.'}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        valid_batches = medicine.batches.filter(
            expiry_date__gt=today, quantity__gt=0, is_quarantined=False
        ).order_by('expiry_date')

        remaining = requested_quantity
        dispensed_details = []

        for batch in valid_batches:
            if remaining == 0: break
            if batch.quantity <= remaining:
                dispensed_details.append({'batch_id': batch.batch_id, 'quantity': batch.quantity})
                remaining -= batch.quantity
                batch.quantity = 0
            else:
                dispensed_details.append({'batch_id': batch.batch_id, 'quantity': remaining})
                batch.quantity -= remaining
                remaining = 0
            batch.save()

        # Twist Level 3: Check Threshold and Create Notification Alert
        if medicine.total_sellable_stock() < medicine.reorder_threshold:
            Notification.objects.create(
                message=f"ALERT: {medicine.name} stock dropped below threshold ({medicine.reorder_threshold})."
            )

        return Response({
            'message': f'Dispensed {requested_quantity} of {medicine.name}',
            'details': dispensed_details
        }, status=status.HTTP_200_OK)

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['batch_id', 'medicine__name']
    ordering_fields = ['expiry_date', 'quantity']

# --- THE FIX: FOOLPROOF CLASS-BASED VIEWS FOR TWISTS ---

class ClockJobView(APIView):
    # This forcibly disables all authentication for this specific endpoint
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Twist Level 1: Automates quarantine and flags expiring stock."""
        today = timezone.now().date()
        seven_days = today + timedelta(days=7)

        expired = Batch.objects.filter(expiry_date__lte=today, is_quarantined=False, quantity__gt=0)
        quarantined_count = expired.count()
        expired.update(is_quarantined=True)

        flagged_count = Batch.objects.filter(
            expiry_date__gt=today, expiry_date__lte=seven_days, is_quarantined=False, quantity__gt=0
        ).count()

        return Response({"flagged": flagged_count, "quarantined": quarantined_count}, status=status.HTTP_200_OK)

class ImportMessyBatchesView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Twist Level 2: Imports messy data, handles nulls, string quantities, and mixed date formats."""
        batches = request.data if isinstance(request.data, list) else request.data.get('batches', [])
        imported, deduped, rejected = 0, 0, 0

        for item in batches:
            try:
                if not all([item.get('medicine_id'), item.get('batch_id'), item.get('quantity'), item.get('expiry_date')]):
                    rejected += 1
                    continue

                medicine_id = item['medicine_id']
                batch_id = str(item['batch_id']).strip()

                qty_match = re.search(r'\d+', str(item['quantity']))
                if not qty_match:
                    rejected += 1
                    continue
                quantity = int(qty_match.group())

                date_str = str(item['expiry_date']).strip()
                if '/' in date_str:
                    parsed_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                else:
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                if Batch.objects.filter(batch_id=batch_id).exists():
                    deduped += 1
                    continue

                medicine = Medicine.objects.get(id=medicine_id)
                Batch.objects.create(medicine=medicine, batch_id=batch_id, quantity=quantity, expiry_date=parsed_date)
                imported += 1
            except Exception:
                rejected += 1

        return Response({"imported": imported, "deduped": deduped, "rejected": rejected}, status=status.HTTP_200_OK)

class OutboxView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """Twist Level 3: Outputs the notification alerts."""
        notifications = Notification.objects.all().values('id', 'message', 'created_at')
        return Response(list(notifications), status=status.HTTP_200_OK)

# --- UI ROUTES ---
def landing_page(request): return render(request, 'inventory/landing.html')
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect('dashboard')
    else: form = UserCreationForm()
    return render(request, 'inventory/register.html', {'form': form})
@login_required(login_url='/login/')
def dashboard(request): return render(request, 'inventory/dashboard.html')