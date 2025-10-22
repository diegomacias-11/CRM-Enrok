from django import forms
from .models import DocumentoActivacion
from clientes.models import Cliente


class DocumentoActivacionForm(forms.ModelForm):
    class Meta:
        model = DocumentoActivacion
        fields = ['tipo_documento', 'descripcion', 'archivo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔒 Lista fija de documentos
        DOCS_ACTIVACION = [
            ('Carta de afiliación CONFEDIN', 'Carta de afiliación CONFEDIN'),
            ('Contrato de futura representación CONDEFIN', 'Contrato de futura representación CONDEFIN'),
            ('Escrito de presentación del programa STPS', 'Escrito de presentación del programa STPS'),
            ('Carátula del programa especial de productividad y competitividad', 'Carátula del programa especial de productividad y competitividad'),
            ('Solicitud del análisis para la implementación del programa de productividad', 'Solicitud del análisis para la implementación del programa de productividad'),
            ('Convocatoria para la celebración de una asamblea en la CMPCA', 'Convocatoria para la celebración de una asamblea en la CMPCA'),
            ('Notificación de asamblea', 'Notificación de asamblea'),
            ('Notificación de asamblea a trabajadores', 'Notificación de asamblea a trabajadores'),
            ('1er Asamblea del programa del productividad en la CMPCA', '1er Asamblea del programa del productividad en la CMPCA'),
            ('2da Asamblea del programa del productividad en la CMPCA', '2da Asamblea del programa del productividad en la CMPCA'),
            ('Dictamen de factibilidad', 'Dictamen de factibilidad'),
            ('Avocamiento programa de productividad SE', 'Avocamiento programa de productividad SE'),
            ('Avocamiento programa de productividad STPS', 'Avocamiento programa de productividad STPS'),
        ]

        self.fields['tipo_documento'] = forms.ChoiceField(
            label="Tipo de documento",
            choices=DOCS_ACTIVACION,
            required=True
        )

        # Ocultar campo cliente (lo maneja la vista)
        if 'cliente' in self.fields:
            self.fields['cliente'].widget = forms.HiddenInput()

        # Bloquear archivo si es edición
        if kwargs.get("instance") and kwargs["instance"].pk:
            self.fields['archivo'].disabled = True
