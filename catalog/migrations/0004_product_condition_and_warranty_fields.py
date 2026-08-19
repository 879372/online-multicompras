import django.db.models.deletion
from django.db import migrations, models


def create_default_condition(apps, schema_editor):
    ProductCondition = apps.get_model('catalog', 'ProductCondition')
    Product = apps.get_model('catalog', 'Product')
    condition, _ = ProductCondition.objects.get_or_create(name='Não informado')
    for name in ('Novo/Lacrado', 'Seminovo', 'Seminovo Premium'):
        ProductCondition.objects.get_or_create(name=name)
    Product.objects.filter(condition__isnull=True).update(condition=condition)


class Migration(migrations.Migration):
    dependencies = [('catalog', '0003_category_product_category_and_image')]

    operations = [
        migrations.CreateModel(
            name='ProductCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ('name',)},
        ),
        migrations.AddField(model_name='product', name='brand', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='product', name='color', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='product', name='condition', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='catalog.productcondition')),
        migrations.AddField(model_name='product', name='model', field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name='product', name='purchase_price', field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
        migrations.AddField(model_name='product', name='storage', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='product', name='warranty_months', field=models.PositiveSmallIntegerField(default=0)),
        migrations.RunPython(create_default_condition, migrations.RunPython.noop),
        migrations.AlterField(model_name='product', name='condition', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='catalog.productcondition')),
    ]
