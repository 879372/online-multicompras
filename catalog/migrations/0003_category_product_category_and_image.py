import django.db.models.deletion
from django.db import migrations, models


def migrate_categories(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    Product = apps.get_model('catalog', 'Product')

    fallback = None
    for product in Product.objects.all().iterator():
        name = (product.category_legacy or '').strip()
        if not name:
            if fallback is None:
                fallback, _ = Category.objects.get_or_create(name='Sem categoria')
            category = fallback
        else:
            category, _ = Category.objects.get_or_create(name=name)
        product.category = category
        # URLField values point outside the managed storage and cannot be
        # converted into uploaded files automatically.
        product.image = None
        product.save(update_fields=['category', 'image'])


class Migration(migrations.Migration):
    dependencies = [('catalog', '0002_product_commerce_fields')]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name_plural': 'categories', 'ordering': ('name',)},
        ),
        migrations.RenameField(
            model_name='product',
            old_name='category',
            new_name='category_legacy',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='catalog.category',
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/%Y/%m/'),
        ),
        migrations.RunPython(migrate_categories, migrations.RunPython.noop),
        migrations.RemoveField(model_name='product', name='category_legacy'),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='catalog.category',
            ),
        ),
    ]
