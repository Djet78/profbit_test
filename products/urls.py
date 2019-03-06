from django.urls import path
from .views import MostPurchasedView, SelectedTimeOrderView


app_name = 'products'

urlpatterns = [
    path('time_range/', SelectedTimeOrderView.as_view(), name='time_range_report'),
    path('most_purchased/', MostPurchasedView.as_view(), name='most_purchased_report'),
]
