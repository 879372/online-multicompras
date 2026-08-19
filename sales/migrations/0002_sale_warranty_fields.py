from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('sales', '0001_initial'), ('catalog', '0004_product_condition_and_warranty_fields')]

    operations = [
        migrations.AddField(model_name='sale', name='customer_city', field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name='saleitem', name='battery_health', field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='saleitem', name='brand', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='saleitem', name='color', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='saleitem', name='condition_name', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='saleitem', name='imei', field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name='saleitem', name='model', field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name='saleitem', name='serial_number', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='saleitem', name='storage', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='saleitem', name='unit_cost', field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
        migrations.AddField(model_name='saleitem', name='warranty_months', field=models.PositiveSmallIntegerField(default=0)),
    ]
