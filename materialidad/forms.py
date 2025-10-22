from django import forms
from .models import DocumentoMaterialidad
from clientes.models import Cliente

class DocumentoMaterialidadForm(forms.ModelForm):
    tipo_persona = forms.CharField(
        label="Tipo de persona",
        required=False,
        disabled=True,
        widget=forms.HiddenInput()  # 👈 Oculto visualmente
    )

    class Meta:
        model = DocumentoMaterialidad
        fields = ['tipo_persona', 'tipo_documento', 'descripcion', 'archivo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        cliente = None
        if "initial" in kwargs and isinstance(kwargs["initial"].get("cliente"), Cliente):
            cliente = kwargs["initial"]["cliente"]
        elif "instance" in kwargs and kwargs["instance"]:
            cliente = kwargs["instance"].cliente

        super().__init__(*args, **kwargs)

        # 👇 Ocultar el campo cliente (ya se asigna en la vista)
        # No se muestra en el form
        if 'cliente' in self.fields:
            self.fields['cliente'].widget = forms.HiddenInput()

        # Definir opciones según tipo de persona
        if cliente:
            tipo = cliente.tipo_persona.lower().strip()
            self.fields['tipo_persona'].initial = cliente.tipo_persona

            if tipo in ['persona física', 'fisica']:
                choices = [
                    ('CSF', 'CSF'),
                    ('INE', 'INE'),
                    ('Comprobante de Domicilio', 'Comprobante de Domicilio'),
                    ('Datos Generales', 'Datos Generales'),
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

        self.fields['tipo_documento'] = forms.ChoiceField(
            label="Tipo de documento",
            choices=choices,
            required=True
        )

        # Bloquear archivo si estamos editando
        if kwargs.get("instance") and kwargs["instance"].pk:
            self.fields['archivo'].disabled = True
