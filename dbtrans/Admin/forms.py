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

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)


