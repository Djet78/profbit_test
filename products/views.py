from django.db import connection
from django.db.models import DecimalField, Sum, F
from django.shortcuts import render
from django.views import View

from .models import Order, OrderItem
from .forms import OrderDateRangeForm


class SelectedTimeOrderView(View):
    template_name = 'products/time_range_report.html'
    search_form = OrderDateRangeForm
    model = Order

    FORM_FIELDS_QUERIES_MAPPING = {
        'from_date': 'created_date__gte',
        'until_date': 'created_date__lte',
    }

    def get(self, request, *args, **kwargs):
        """ Renders report with orders within asked time, or for all the time if time wan't specified. """

        if not request.GET:
            context = {
                    'search_form': self.search_form(),
                    'orders': self._get_query(),
                }
        else:
            search_form = self.search_form(request.GET)
            context = {'search_form': search_form}

            if search_form.is_valid():
                requested = {**search_form.cleaned_data}
                query_params = {
                    self.FORM_FIELDS_QUERIES_MAPPING[field]: value for field, value in requested.items() if value
                }
                context['orders'] = self._get_query(**query_params)

        #   Force query execution in order to have connections amount value below.
        # Reason: Since queries are lazy, i can't put connections amount value to the top of the
        # page, because in natural way query will be executed after it. And view will use cached
        # query, so connections amount will be the same.
        bool(context['orders'])
        context['connections'] = len(connection.queries)

        return render(request, self.template_name, context)

    def _get_query(self, **query_params):
        orders = self.model.objects.filter(**query_params).annotate(
            total_cost=Sum(F('items__product_price') * F('items__amount'), output_field=DecimalField())
        ).prefetch_related('items')
        return orders


class MostPurchasedView(View):
    template_name = 'products/most_purchased_report.html'

    TOP_N_SLICE = 100

    def get(self, request, *args, **kwargs):
        """ Renders view with 'self.TOP_N_SLICE' most sold products related data. """

        context = {'report': self._get_report()}

        # DB Trigger
        bool(context['report'])
        context['connections'] = len(connection.queries)

        return render(request, self.template_name, context)

    def _get_report(self):
        """ Generates dict with data for report

        Dict format: {
            'prod_name_1': [
                {
                    'order_number': record_num,
                    'price': record_price,
                    'order_dt': record_datetime,
                },
                {
                    Other records associated to product...
                },
            ],
            'prod_name_n': [
                ...
            ]
        }
        """
        # This approach limits db hits to 2, but have bad memory and time complexity.
        # I'll try to find something better than that.

        top_sellers = OrderItem.objects.values_list('product_name', flat=True) \
                                       .annotate(total_selled=Sum('amount')) \
                                       .order_by('-total_selled')[:self.TOP_N_SLICE]

        order_items_records = OrderItem.objects.select_related().filter(product_name__in=list(top_sellers))

        report = {}

        for record in order_items_records.iterator():
            # Using 'in' here because it works faster than dict.get() method.
            if record.product_name not in report:
                report[record.product_name] = []
            else:
                report[record.product_name].append(
                    {
                        'price': record.product_price,
                        'order_number': record.order.number,
                        'order_dt': record.order.created_date,
                    }
                )

        return report
