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

        return render(request, self.template_name, context)

    def _get_query(self, **query_params):
        return self.model.objects.select_related().filter(**query_params)


class MostPurchasedView(View):
    template_name = 'products/most_purchased_report.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)
