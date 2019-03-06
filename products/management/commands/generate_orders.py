from datetime import datetime, timedelta
from random import randint

from django.core.management.base import BaseCommand, CommandError
from products.models import Order, OrderItem


class Command(BaseCommand):
    help = 'Generate given amount of orders'
    requires_migrations_checks = True
    START_DATE = datetime(2018, 1, 1, 9)
    TIME_STEP = timedelta(hours=1)

    def add_arguments(self, parser):
        parser.add_argument('orders_amount', type=int)

    def handle(self, *args, **options):
        orders_amount = options.get('orders_amount')
        if orders_amount <= 0:
            raise CommandError('"orders_amount" argument must be bigger than 0!')

        for iter_num in range(orders_amount + 1):
            order_time = self.START_DATE + (self.TIME_STEP * iter_num)
            curr_order = Order.objects.create(number=iter_num, created_date=order_time)

            for order_item in range(1, randint(1, 5) + 1):
                OrderItem.objects.create(order=curr_order,
                                         product_name='Product-{}'.format(order_item),
                                         product_price=randint(100, 9999),
                                         amount=randint(1, 10))
