from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cash_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='compare_at_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='installments',
            field=models.PositiveSmallIntegerField(default=12),
        ),
        migrations.AddField(
            model_name='product',
            name='variants',
            field=models.JSONField(blank=True, default=list, help_text='Product options such as model, color and stock. Stored as a list of objects.'),
        ),
    ]
