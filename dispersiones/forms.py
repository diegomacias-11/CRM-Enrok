from django import forms
from .models import Dispersion

class DispersionForm(forms.ModelForm):
    estatus_proceso = forms.ChoiceField(choices=[
        ('Pendiente', 'Pendiente'),
        ('Enviada', 'Enviada'),
        ('Aplicada', 'Aplicada'),        
    ])
    estatus_periodo = forms.ChoiceField(choices=[
        ('Pendiente', 'Pendiente'),
        ('Cerrado', 'Cerrado'),
        ('Timbrado', 'Timbrado'),        
        ('Enviado', 'Enviado'), 
        ('Enviado ind.', 'Enviado ind.'), 
        ('Drive', 'Drive'), 
    ])

    class Meta:
        model = Dispersion  
        fields = [
            'fecha','cliente', 'num_factura', 'monto', 'num_factura_honorarios',
            'estatus_proceso', 'num_periodo', 'estatus_periodo', 'comentarios',
        ]
        labels = {
            'num_factura_honorarios': 'Número de factura honorarios',
            'num_factura': 'Número de factura',
            'num_periodo': 'Número de periodo',
        }
        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 3}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Recibir mes y anio desde la vista
        self.mes = kwargs.pop('mes', None)
        self.anio = kwargs.pop('anio', None)
        super().__init__(*args, **kwargs)

        # Si es edición de un registro existente, monto y cliente no editables
        if self.instance and self.instance.pk:
            self.fields['monto'].disabled = True
            self.fields['cliente'].disabled = True

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and self.mes and self.anio:
            if fecha.month != self.mes or fecha.year != self.anio:
                raise forms.ValidationError(f"La fecha debe pertenecer al mes {self.mes:02d}/{self.anio}.")
        return fecha
