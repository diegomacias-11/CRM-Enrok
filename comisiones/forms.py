from django import forms
from .models import Pago
from datetime import date

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'fecha_pago', 'comentarios']
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date', 'max': date.today()}),
            'comentarios': forms.Textarea(attrs={'rows':2}),
        }