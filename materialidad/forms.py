from django import forms
from .models import DocumentoMaterialidad
from clientes.models import Cliente


class DocumentoMaterialidadForm(forms.ModelForm):
    tipo_persona = forms.CharField(
        label="Tipo de persona",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = DocumentoMaterialidad
        fields = ['cliente', 'tipo_persona', 'tipo_documento', 'descripcion', 'archivo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔒 Bloquear el campo 'cliente'
        self.fields['cliente'].disabled = True

        # Deshabilitar archivo si estamos editando
        if self.instance and self.instance.pk:
            self.fields['archivo'].disabled = True

        cliente = None

        # Obtener el cliente desde initial o la instancia
        if 'cliente' in self.initial and isinstance(self.initial['cliente'], Cliente):
            cliente = self.initial['cliente']
        elif self.instance and self.instance.pk:
            cliente = self.instance.cliente

        # Si hay cliente, usar su tipo_persona para definir opciones
        if cliente:
            tipo = cliente.tipo_persona.lower().strip()
            self.fields['tipo_persona'].initial = cliente.tipo_persona

            if tipo in ['persona física', 'fisica']:
                choices = [
                    ('csf', 'CSF'),
                    ('ine', 'INE'),
                    ('domicilio', 'Comprobante de Domicilio'),
                    ('generales', 'Datos Generales'),
                ]
            else:
                choices = [
                    ('Acta Constitutiva', 'Acta Constitutiva'),
                    ('Poder', 'Poder'),
                    ('Identificación del Apoderado', 'Identificación del Apoderado'),
                    ('Comprobante de Domicilio', 'Comprobante de Domicilio'),
                    ('RFC', 'RFC'),
                    ('Opinión de Cumplimiento de Obligaciones Fiscales', 'Opinión de Cumplimiento de Obligaciones Fiscales'),
                    ('CSF', 'CSF'),
                ]
        else:
            self.fields['tipo_persona'].initial = "—"
            choices = []

        # Asignar opciones del tipo de documento
        self.fields['tipo_documento'] = forms.ChoiceField(
            label="Tipo de documento",
            choices=choices,
            required=True
        )
