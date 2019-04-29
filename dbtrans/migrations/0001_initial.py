# Generated by Django 2.2 on 2019-04-23 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslatedField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obj_id', models.PositiveIntegerField()),
                ('field', models.CharField(max_length=50, verbose_name='Campo')),
                ('changed', models.BooleanField(default=True)),
                ('ct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Modelo')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang_code', models.CharField(max_length=10, verbose_name='Language Code')),
                ('translation', models.TextField(blank=True, default='', null=True)),
                ('updated', models.BooleanField(default=False, verbose_name='Fuzzy')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dbtrans.TranslatedField', verbose_name='Field')),
            ],
            options={
                'permissions': (('can_translate_to_en-us', 'User can translato to None language'), ('can_translate_to_ch-ci', 'User can translato to None language')),
                'unique_together': {('field', 'lang_code')},
            },
        ),
    ]
