from django.db import models


class Order(models.Model):
    number = models.IntegerField()
    created_date = models.DateTimeField()

    class Meta:
        ordering = ('-created_date', )

    def __str__(self):
        return '{} - {}'.format(self.pk, self.created_date)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=50)
    product_price = models.DecimalField(max_digits=6, decimal_places=2)
    amount = models.SmallIntegerField()

    def __str__(self):
        return '{}: {}'.format(self.order, self.product_name)
