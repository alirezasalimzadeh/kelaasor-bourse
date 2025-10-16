from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Company(models.Model):
    symbol = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=128)
    total_shares = models.PositiveBigIntegerField()


class InstrumentStats(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    ref_price = models.DecimalField(max_digits=18, decimal_places=2)
    band_low = models.DecimalField(max_digits=18, decimal_places=2)
    band_high = models.DecimalField(max_digits=18, decimal_places=2)
    last_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


class Holding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField()

    class Meta:
        unique_together = ('user', 'company')


class Order(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TYPES = [(BUY, 'BUY'), (SELL, 'SELL')]

    OPEN = 'OPEN'
    PART = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    STATUS = [(OPEN, OPEN), (PART, PART), (FILLED, FILLED), (CANCELED, CANCELED)]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TYPES)
    quantity = models.PositiveBigIntegerField()
    quantity_filled = models.PositiveBigIntegerField(default=0)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining(self):
        return self.quantity - self.quantity_filled
