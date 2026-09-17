from django.db import models
from django.utils import timezone

class Medicine(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    
    def total_sellable_stock(self):
        # Calculates only stock that is NOT expired and has quantity > 0
        today = timezone.now().date()
        valid_batches = self.batches.filter(expiry_date__gt=today, quantity__gt=0)
        return sum(batch.quantity for batch in valid_batches)

    def __str__(self):
        return self.name

class Batch(models.Model):
    medicine = models.ForeignKey(Medicine, related_name='batches', on_delete=models.CASCADE)
    batch_id = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Guarantees FEFO (First-Expiry-First-Out) sorting automatically
        ordering = ['expiry_date']

    def is_expired(self):
        return self.expiry_date <= timezone.now().date()

    def __str__(self):
        return f"{self.batch_id} - {self.medicine.name} (Qty: {self.quantity})"