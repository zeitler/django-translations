from django.forms import ModelForm, Textarea
from django.forms.utils import ErrorList

from dbtrans.models import Translation


class TranslationAdminForm(ModelForm):
    class Meta:
        model = Translation
        fields = '__all__'
        widgets = {
            'translation': Textarea(attrs={'cols': "60", 'rows': "1,1"}),
        }
        help_texts = {
            'translation': 'asddsa',
        }
