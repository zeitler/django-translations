# django-translations
A django app that powers model fields with translations invisible to the model database table

When we have several models with fields that require translations, we have to create other fields for the specific language. 

With this app we just have to register it in INSTALLED_APPS,
and use a decorator in the model we want to translate. It will be created other models that stores all the translations.
The user that uses the Admin will see always the translation that is selected in the browser.

There is an admin app that allow us to translate all the fields.

Example:

<models.py>
...
from dbtrans.decorator import Translate

@Translate('name', 'observations')
class Category(models.Model):
    name = models.CharField(max_length=20, verbose_name='Name')
    observations = models.TextField(max_length=200, verbose_name='Observations')
...

And that's it!

Only supports CharField and TextField.

There is another app called TestsApp if you want to see how it works that have a place to change languages because admin don't 
have how to change language.
This app isn't necessary to the dbtrans app. You can delete it and try on your own apps.
Don't forget to add it to INSTALLED_APPS and do all the migrations


