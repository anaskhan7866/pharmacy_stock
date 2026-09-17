from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Medicine, Batch
from .serializers import MedicineSerializer, BatchSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

    # Custom API endpoint for FEFO dispensing: /api/medicines/<id>/dispense/
    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        medicine = self.get_object()
        try:
            requested_quantity = int(request.data.get('quantity', 0))
        except ValueError:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        if requested_quantity <= 0:
            return Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

        if medicine.total_sellable_stock() < requested_quantity:
            return Response({'error': 'Insufficient valid stock. Check for expired batches.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get valid batches ordered by expiry date (FEFO)
        today = timezone.now().date()
        valid_batches = medicine.batches.filter(expiry_date__gt=today, quantity__gt=0).order_by('expiry_date')

        remaining_to_dispense = requested_quantity
        dispensed_details = []

        for batch in valid_batches:
            if remaining_to_dispense == 0:
                break
            
            if batch.quantity <= remaining_to_dispense:
                dispensed_details.append({'batch_id': batch.batch_id, 'quantity': batch.quantity})
                remaining_to_dispense -= batch.quantity
                batch.quantity = 0
                batch.save()
            else:
                dispensed_details.append({'batch_id': batch.batch_id, 'quantity': remaining_to_dispense})
                batch.quantity -= remaining_to_dispense
                batch.save()
                remaining_to_dispense = 0

        return Response({
            'message': f'Successfully dispensed {requested_quantity} of {medicine.name}',
            'details': dispensed_details
        }, status=status.HTTP_200_OK)

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer