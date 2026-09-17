from django.db import models
from django.utils import timezone

class Medicine(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    reorder_threshold = models.PositiveIntegerField(default=50) # Level 3

    def total_sellable_stock(self):
        today = timezone.now().date()
        # Level 1: Ensure we don't count quarantined stock
        valid_batches = self.batches.filter(expiry_date__gt=today, quantity__gt=0, is_quarantined=False)
        return sum(batch.quantity for batch in valid_batches)

    def __str__(self):
        return self.name

class Batch(models.Model):
    medicine = models.ForeignKey(Medicine, related_name='batches', on_delete=models.CASCADE)
    batch_id = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_quarantined = models.BooleanField(default=False) # Level 1

    class Meta:
        ordering = ['expiry_date']

    def is_expired(self):
        return self.expiry_date <= timezone.now().date()

    def __str__(self):
        return f"{self.batch_id} - {self.medicine.name} (Qty: {self.quantity})"

# Level 3: Notification Service Outbox
class Notification(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message