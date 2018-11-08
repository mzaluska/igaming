from django import forms


class DepositForm(forms.Form):
    amount = forms.IntegerField(min_value=0, required=True)
