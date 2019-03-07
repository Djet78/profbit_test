from django.db import connection
from django.db.models import Sum, F, DecimalField
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
        if context['orders']:
            pass
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
        """ Renders view with 'self.TOP_N_SLICE' sold products """

        # I don't like this solution, because it hits db for every product in a list.
        # But this is the one I've ended up with. Would be worse if i did't implement task at all, I think.
        # I'll try to found better solution for this.

        top_sellers = OrderItem.objects.values('product_name') \
                               .annotate(total_selled=Sum('amount')) \
                               .order_by('-total_selled')[:self.TOP_N_SLICE]

        for prod in top_sellers:
            prod['orders'] = OrderItem.objects.filter(product_name=prod['product_name']).select_related()

            # DB Trigger, like in the view above
            if prod['orders']:
                pass

        context = {
            'connections': len(connection.queries),
            'top_sellers': top_sellers,
        }

        return render(request, self.template_name, context)
