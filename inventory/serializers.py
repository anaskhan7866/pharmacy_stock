from rest_framework import serializers
from .models import Medicine, Batch

class MedicineSerializer(serializers.ModelSerializer):
    # This automatically includes the sellable stock calculation in the API response
    total_sellable_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'description', 'total_sellable_stock']

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'