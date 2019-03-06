from django import forms


class OrderDateRangeForm(forms.Form):
    from_date = forms.DateTimeField(required=False)
    until_date = forms.DateTimeField(required=False)
