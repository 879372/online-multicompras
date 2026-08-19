WARRANTY_RULES = (
    {
        'key': 'xiaomi',
        'brands': ('xiaomi', 'redmi', 'poco'),
        'conditions': None,
        'months': 6,
        'provider': 'AstroTech',
        'label': 'Xiaomi, Redmi e Poco: 6 meses de garantia pela loja',
    },
    {
        'key': 'iphone_new',
        'brands': ('apple', 'iphone'),
        'conditions': ('novo/lacrado',),
        'months': 12,
        'provider': 'Fabricante',
        'label': 'iPhone novo/lacrado: 1 ano de garantia',
    },
    {
        'key': 'iphone_preowned_premium',
        'brands': ('apple', 'iphone'),
        'conditions': ('seminovo premium',),
        'months': 6,
        'provider': 'AstroTech',
        'label': 'iPhone seminovo premium: 6 meses de garantia pela loja',
    },
    {
        'key': 'iphone_preowned',
        'brands': ('apple', 'iphone'),
        'conditions': ('seminovo',),
        'months': 4,
        'provider': 'AstroTech',
        'label': 'iPhone seminovo: 4 meses de garantia pela loja',
    },
)


def resolve_warranty(brand='', model='', condition=''):
    identity = f'{brand} {model}'.casefold()
    condition_name = condition.casefold().strip()
    for rule in WARRANTY_RULES:
        if not any(term in identity for term in rule['brands']):
            continue
        if rule['conditions'] is not None and condition_name not in rule['conditions']:
            continue
        return rule
    return None


def public_warranty_rules():
    return [
        {key: rule[key] for key in ('key', 'months', 'provider', 'label')}
        for rule in WARRANTY_RULES
    ]
