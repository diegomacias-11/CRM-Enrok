from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    servicio = forms.ChoiceField(choices=[
        ('PROCOM', 'PROCOM'),
    ])

    factura = forms.ChoiceField(choices=[
        ('CONFEDIN', 'CONFEDIN'),
        ('ZAMORA', 'ZAMORA'),
        ('SERVIARUGA', 'SERVIARUGA'),
        ('CAMARENCE', 'CAMARENCE'),
        ('HATRES', 'HATRES'),
    ])

    tipo_persona = forms.ChoiceField(choices=[
        ('Persona Física', 'Persona Física'),
        ('Persona Moral', 'Persona Moral'),
    ])

    class Meta:
        model = Cliente
        fields = [
            'servicio', 'comision_procom', 'factura', 'nombre', 'tipo_persona', 'utilidad_enrok',
            'comisionista_1', 'porcentaje_1',
            'comisionista_2', 'porcentaje_2',
            'comisionista_3', 'porcentaje_3',
            'comisionista_4', 'porcentaje_4',
            'comisionista_5', 'porcentaje_5',
            'comisionista_6', 'porcentaje_6',
            'comisionista_7', 'porcentaje_7',
            'comisionista_8', 'porcentaje_8',
            'comisionista_9', 'porcentaje_9',
        ]
