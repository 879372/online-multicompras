from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Category, Product, ProductCondition, Supplier, SupplierOffer


UNKNOWN = 'Fornecedor não identificado (lista 19/08/2026)'

# supplier, brand, model, ram, storage, network, condition, cost, colors,
# warranty months, warranty provider, seal, origin, known stock
ROWS = [
    (UNKNOWN, 'Xiaomi', 'Redmi Pad 2 11', '8 GB', '256 GB', '', 'Novo/Lacrado', 1350, ['Cinza'], 0, '', False, '', 1),
    (UNKNOWN, 'Xiaomi', 'Poco C71', '4 GB', '128 GB', '', 'Novo/Lacrado', 760, ['Laranja', 'Azul', 'Preto'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Poco C81 Pro', '4 GB', '256 GB', '', 'Novo/Lacrado', 900, ['Verde', 'Preto', 'Laranja'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Redmi Note 15', '8 GB', '512 GB', '', 'Novo/Lacrado', 1400, ['Roxo', 'Verde', 'Preto', 'Azul-claro'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Redmi Note 15', '8 GB', '256 GB', '5G', 'Novo/Lacrado', 1500, ['Azul'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Redmi Note 15 Pro', '8 GB', '256 GB', '5G', 'Novo/Lacrado', 1880, ['Preto', 'Cinza'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Poco X7', '12 GB', '512 GB', '', 'Novo/Lacrado', 1850, ['Preto'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Poco X7 Pro', '8 GB', '256 GB', '', 'Novo/Lacrado', 1870, ['Amarelo', 'Verde', 'Preto'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Poco X7 Pro', '12 GB', '256 GB', '5G', 'Novo/Lacrado', 1950, ['Amarelo'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Poco X7 Pro', '12 GB', '512 GB', '', 'Novo/Lacrado', 2200, ['Verde', 'Preto'], 0, '', False, '', None),
    (UNKNOWN, 'Xiaomi', 'Poco F8 Pro', '12 GB', '512 GB', '', 'Novo/Lacrado', 3600, ['Preto'], 0, '', False, '', None),
    (UNKNOWN, 'Realme', 'Realme Note 70', '4 GB', '128 GB', '', 'Novo/Lacrado', 780, ['Preto', 'Laranja'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme 100i NFC', '4 GB', '128 GB', 'NFC', 'Novo/Lacrado', 980, ['Cinza'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme P4 Lite', '4 GB', '256 GB', '', 'Novo/Lacrado', 1050, ['Cinza', 'Roxo'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme 100x NFC', '4 GB', '128 GB', 'NFC', 'Novo/Lacrado', 1070, ['Azul', 'Laranja'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme C85 NFC', '6 GB', '128 GB', 'NFC', 'Novo/Lacrado', 1200, ['Azul', 'Preto'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme C85 NFC', '8 GB', '256 GB', 'NFC', 'Novo/Lacrado', 1350, ['Preto', 'Azul'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme C85 Pro NFC', '8 GB', '256 GB', 'NFC', 'Novo/Lacrado', 1550, ['Roxo', 'Verde'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme C85', '8 GB', '256 GB', '5G', 'Novo/Lacrado', 1700, ['Roxo'], 12, 'Fabricante', False, '', None),
    (UNKNOWN, 'Realme', 'Realme 14 Pro Plus', '12 GB', '512 GB', '', 'Novo/Lacrado', 2500, ['Branco'], 12, 'Fabricante', False, '', None),
    ('RM Cell', 'Apple', 'iPhone 13', '', '128 GB', '', 'Seminovo', 1800, ['Black', 'Red'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 14 Pro', '', '256 GB', '', 'Seminovo', 2950, ['Purple'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 14 Pro Max', '', '128 GB', '', 'Seminovo', 3200, [('Black', 3200), ('Purple', 3300)], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 14 Pro Max', '', '256 GB', '', 'Seminovo', 3400, ['Black'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 15', '', '128 GB', '', 'Seminovo', 2700, ['Black'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 15 Pro', '', '128 GB', '', 'Seminovo', 3500, ['Black'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 15 Pro', '', '256 GB', '', 'Seminovo', 3750, ['Black'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 15 Plus', '', '128 GB', '', 'Seminovo', 2850, ['Black'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 15 Pro Max', '', '256 GB', '', 'Seminovo', 4200, ['Black'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 16', '', '128 GB', '', 'Seminovo', 3800, ['Black', 'Blue'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 16 Pro', '', '128 GB', '', 'Seminovo', 4400, ['Black'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('RM Cell', 'Apple', 'iPhone 16 Plus', '', '128 GB', '', 'Seminovo', 3900, ['Black', 'Blue'], 1, 'RM Cell', True, 'Estados Unidos', None),
    ('ASIS', 'Apple', 'iPhone 16', '', '256 GB', '', 'Não informado', 4050, ['White'], 6, 'RM Cell', True, '', None),
    ('ASIS', 'Apple', 'iPhone 16 Pro', '', '128 GB', '', 'Não informado', 4400, ['White'], 6, 'RM Cell', True, '', None),
    ('ASIS', 'Apple', 'iPhone 16 Pro', '', '256 GB', '', 'Não informado', 4700, ['White'], 6, 'RM Cell', True, '', None),
    ('ASIS', 'Apple', 'iPhone 16 Pro Max', '', '256 GB', '', 'Não informado', 5300, ['Desert', 'Black'], 6, 'RM Cell', True, '', None),
    ('Tony Cell', 'Realme', 'Realme Note 60X', '4 GB', '128 GB', '4G', 'Novo/Lacrado', 730, ['Verde', 'Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Realme', 'Realme C75', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1280, ['Dourado'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Realme', 'Realme C85 Pro', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1530, ['Preto', 'Roxo'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Realme', 'Realme C85', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1400, ['Preto', 'Azul'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Realme', 'Realme C71', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1050, ['Branco', 'Verde'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi A7 Pro', '4 GB', '128 GB', '4G', 'Novo/Lacrado', 760, ['Preto', 'Dourado'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi 15C', '4 GB', '256 GB', '4G', 'Novo/Lacrado', 900, ['Preto', 'Azul', 'Verde'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi 15C', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1000, ['Preto', 'Azul', 'Laranja'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi 15', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1140, ['Preto', 'Prata', 'Roxo'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi Pad 2', '4 GB', '128 GB', '4G', 'Novo/Lacrado', 1130, ['Verde', 'Cinza'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi Pad 2', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1350, ['Cinza'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi Note 15', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1250, ['Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi Note 15 Pro', '8 GB', '256 GB', '4G', 'Novo/Lacrado', 1600, ['Cinza', 'Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi Note 15 Pro Plus', '8 GB', '256 GB', '5G', 'Novo/Lacrado', 2350, ['Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Redmi Note 15 Pro', '8 GB', '256 GB', '5G', 'Novo/Lacrado', 1800, ['Preto', 'Azul'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco C71', '4 GB', '128 GB', '4G', 'Novo/Lacrado', 750, ['Preto', 'Dourado'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco X8 Pro', '8 GB', '512 GB', '5G', 'Novo/Lacrado', 2480, ['Preto', 'Verde'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco X8 Pro', '8 GB', '256 GB', '5G', 'Novo/Lacrado', 2200, ['Preto', 'Branco'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco X8 Pro', '12 GB', '512 GB', '5G', 'Novo/Lacrado', 2580, ['Branco', 'Verde', 'Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco X8 Pro Max', '12 GB', '512 GB', '5G', 'Novo/Lacrado', 3200, ['Laranja'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco X8 Pro Max', '12 GB', '256 GB', '5G', 'Novo/Lacrado', 2900, ['Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco F7', '12 GB', '512 GB', '5G', 'Novo/Lacrado', 2750, ['Cinza', 'Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco M8 Pro', '8 GB', '256 GB', '5G', 'Novo/Lacrado', 1650, ['Preto', 'Cinza'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco M8 Pro', '12 GB', '512 GB', '5G', 'Novo/Lacrado', 1850, ['Preto'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco F8 Pro', '12 GB', '512 GB', '5G', 'Novo/Lacrado', 3500, ['Silver', 'Azul'], 0, 'Fabricante', False, '', None),
    ('Tony Cell', 'Xiaomi', 'Poco X8 Pro Homem de Ferro', '12 GB', '512 GB', '5G', 'Novo/Lacrado', 3200, [], 0, 'Fabricante', False, '', None),
]


class Command(BaseCommand):
    help = 'Importa de forma idempotente as listas de fornecedores recebidas em 19/08/2026.'

    def handle(self, *args, **options):
        created_products = created_offers = 0
        for row in ROWS:
            supplier_name, brand, model, ram, storage, network, condition_name, cost, colors, months, provider, seal, origin, stock = row
            supplier, _ = Supplier.objects.get_or_create(name=supplier_name)
            condition, _ = ProductCondition.objects.get_or_create(name=condition_name)
            is_tablet = 'pad' in model.lower()
            category, _ = Category.objects.get_or_create(name='tablet' if is_tablet else 'phone')
            name = ' '.join(part for part in (model, ram, storage, network) if part)
            variants = []
            for color in colors:
                color_name, variant_cost = color if isinstance(color, tuple) else (color, cost)
                variants.append({
                    'color': color_name,
                    'ram': ram,
                    'storage': storage,
                    'connectivity': network,
                    'purchase_price': str(Decimal(variant_cost).quantize(Decimal('0.01'))),
                })
            product, product_created = Product.objects.get_or_create(
                name=name,
                condition=condition,
                defaults={
                    'category': category, 'brand': brand, 'model': model, 'ram': ram,
                    'storage': storage, 'connectivity': network, 'origin': origin,
                    'warranty_months': months, 'warranty_provider': provider,
                    'warranty_requires_seal': seal, 'purchase_price': cost,
                    'price': None, 'stock': stock or 0, 'variants': variants, 'is_active': False,
                },
            )
            if product_created:
                created_products += 1
            offer, offer_created = SupplierOffer.objects.update_or_create(
                product=product, supplier=supplier, supplier_sku='',
                defaults={'purchase_price': cost, 'stock': stock, 'variants': variants, 'source_text': 'Lista recebida em 19/08/2026', 'is_available': True},
            )
            created_offers += int(offer_created)
            if product.purchase_price is None or offer.purchase_price < product.purchase_price:
                product.purchase_price = offer.purchase_price
                product.save(update_fields=['purchase_price', 'updated_at'])
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída: {created_products} produtos e {created_offers} ofertas novas; todos os produtos novos estão inativos.'
        ))
