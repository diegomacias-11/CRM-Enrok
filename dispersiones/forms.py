from django import forms
from .models import Dispersion

class DispersionForm(forms.ModelForm):
    factura = forms.ChoiceField(choices=[
        ('CONFEDIN', 'CONFEDIN'),
        ('ASE', 'ASE'),
    ])
    estatus = forms.ChoiceField(choices=[
        ('Enviada', 'Enviada'),
        ('Aplicada', 'Aplicada'),        
    ])
    estatus_periodo = forms.ChoiceField(choices=[
        ('Cerrado', 'Cerrado'),
        ('Timbrado', 'Timbrado'),        
        ('Enviado', 'Enviado'), 
        ('Enviado ind.', 'Enviado ind'), 
        ('Drive', 'Drive'), 
    ])

    class Meta:
        model = Dispersion  
        fields = [
            'fecha','cliente', 'factura', 'factura_honorarios', 'monto',
            'estatus', 'estatus_periodo', 'comentarios'
        ]
        labels = {
            'factura_honorarios': 'Número de factura', 
        }
        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 3}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es edición de un registro existente, monto no editable
        if self.instance and self.instance.pk:
            self.fields['monto'].widget.attrs['readonly'] = True
