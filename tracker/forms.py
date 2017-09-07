from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Bills, Railcars, Tracking


class BillsModelForm(forms.ModelForm):
    class Meta:
        model = Bills
        fields = ['bill', 'amount', 'supplier', 'bill_date', 'supply_date']
        widgets = {
            'bill': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'bill_date': forms.DateInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'supply_date': forms.DateInput(attrs={'class': 'form-control', 'maxlength': '10'}),
        }


class RailcarsModelForm(forms.ModelForm):
    class Meta:
        model = Railcars
        fields = ['railcar', 'fuel', 'volume']

    class Media:
        js = ('jquery.formset.js',)

    def __init__(self, *args, **kwargs):
        super(RailcarsModelForm, self).__init__(*args, **kwargs)
        self.fields['railcar'].widget.attrs = {'class': 'form-control',
                                               'required': True,
                                               'maxlength': '8'}
        self.fields['fuel'].widget.attrs = {'class': 'form-control',
                                            'required': True}
        self.fields['volume'].widget.attrs = {'class': 'form-control',
                                              'required': True}


class TrackingModelForm(forms.ModelForm):
    class Meta:
        model = Tracking
        fields = ['railcar', 'amount', 'comment']

    def __init__(self, *args, **kwargs):
        super(TrackingModelForm, self).__init__(*args, **kwargs)
        self.fields['railcar'].widget.attrs = {'class': 'form-control'}
        self.fields['amount'].widget.attrs = {'class': 'form-control'}
        self.fields['comment'].widget.attrs = {'class': 'form-control'}


class MainLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(MainLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class': 'form-control'}
        self.fields['password'].widget.attrs = {'class': 'form-control'}
