from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Bills, Railcars, Tracking


class BillsModelForm(forms.ModelForm):
    class Meta:
        model = Bills
        fields = ['bill', 'amount', 'supplier', 'volume', 'bill_date', "payment_date"]
        widgets = {
            'bill': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': 600}),
            'bill_date': forms.DateInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            "payment_date": forms.DateInput(attrs={'class': 'form-control', 'maxlength': '10'}),
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
        self.fields['fuel'].empty_label = 'Выберите тип топлива'
        self.fields['volume'].widget.attrs = {'class': 'form-control',
                                              'required': True,
                                              'min': '1',
                                              'max': '60000'}


class RailcarAddForm(forms.ModelForm):
    railcar = forms.ModelChoiceField(label='Вагон', queryset=Railcars.objects.filter(bill=None, is_accepted=True))
    railcar.widget = forms.Select(attrs={'class': 'form-control'})

    class Meta:
        model = Railcars
        fields = ('railcar',)
    # queryset = Railcars.objects.filter(bill=None)

    # class Media:
    #     js = ('jquery.formset.js',)

    # def __init__(self, *args, **kwargs):
    #     super(RailcarsModelForm, self).__init__(*args, **kwargs)
    #     self.fields['railcar'].queryset = Railcars.objects.filter(bill=None)
        # self.fields['railcar'].widget.attrs = {'class': 'form-control',
                                               # 'required': True,
                                               # }


class TrackingModelForm(forms.ModelForm):
    class Meta:
        model = Tracking
        # fields = ['railcar', 'amount', 'comment']
        fields = ['amount', 'comment']

    def __init__(self, *args, **kwargs):
        super(TrackingModelForm, self).__init__(*args, **kwargs)
        # self.fields['railcar'].queryset = Railcars.objects.filter(is_accepted=False).order_by('railcar')
        # self.fields['railcar'].widget.attrs = {'class': 'form-control'}
        # self.fields['railcar'].empty_label = 'Выберите вагон'
        self.fields['amount'].widget.attrs = {'class': 'form-control',
                                              'min': '1',
                                              'max': '60000'}
        self.fields['comment'].widget.attrs = {'class': 'form-control'}


class MainLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(MainLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class': 'form-control'}
        self.fields['password'].widget.attrs = {'class': 'form-control'}
