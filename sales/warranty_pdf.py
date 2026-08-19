import calendar
from datetime import date
from io import BytesIO

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _money(value):
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def _value(value):
    return str(value) if value not in (None, '') else '-'


def build_warranty_pdf(sale):
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterSmall', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, leading=10))
    styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], fontSize=11, leading=13, textColor=colors.HexColor('#ef5b24'), spaceBefore=7, spaceAfter=5))
    styles.add(ParagraphStyle(name='BodySmall', parent=styles['BodyText'], fontSize=8.2, leading=10.5, alignment=TA_JUSTIFY, spaceAfter=4))
    styles.add(ParagraphStyle(name='Tiny', parent=styles['BodyText'], fontSize=7.3, leading=9.2, alignment=TA_JUSTIFY, spaceAfter=3))
    styles.add(ParagraphStyle(name='Signature', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8.5, leading=11))

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#dddddd'))
        canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(18 * mm, 9 * mm, f'{settings.COMPANY_NAME} - Termo de garantia da venda #{sale.id:06d}')
        canvas.drawRightString(192 * mm, 9 * mm, f'Página {document.page}')
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=14 * mm, bottomMargin=19 * mm,
        title=f'Termo de garantia - Venda {sale.id:06d}',
        author=settings.COMPANY_NAME,
    )
    story = []
    sale_date = timezone.localtime(sale.created_at).date()
    header = Table([
        [Paragraph(f'<b>{settings.COMPANY_NAME}</b>', ParagraphStyle(name='Brand', fontName='Helvetica-Bold', fontSize=20, textColor=colors.white)),
         Paragraph('<b>TERMO DE GARANTIA</b><br/>COMPROVANTE DE VENDA', ParagraphStyle(name='DocTitle', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.white))],
    ], colWidths=[72 * mm, 102 * mm])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ef5b24')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.extend([header, Spacer(1, 5 * mm)])
    story.append(Paragraph(f'<b>CNPJ:</b> {settings.COMPANY_CNPJ}<br/><b>ENDEREÇO:</b> {settings.COMPANY_ADDRESS}<br/><b>WHATSAPP:</b> {settings.COMPANY_WHATSAPP}', styles['CenterSmall']))
    story.append(Spacer(1, 4 * mm))
    summary = Table([
        ['CÓDIGO', f'{sale.id:06d}', 'VALOR', _money(sale.total)],
        ['DATA DA VENDA', sale_date.strftime('%d/%m/%Y'), 'STATUS', sale.get_status_display().upper()],
    ], colWidths=[31 * mm, 55 * mm, 31 * mm, 57 * mm])
    summary.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), .5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f3f3')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f3f3f3')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.extend([summary, Paragraph('CLIENTE', styles['Section'])])
    client = Table([
        ['NOME', sale.customer_name], ['TELEFONE', _value(sale.customer_phone)], ['CIDADE', _value(sale.customer_city)],
    ], colWidths=[32 * mm, 142 * mm])
    client.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), .5, colors.HexColor('#cccccc')), ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f3f3')), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8.5), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    story.append(client)

    for index, item in enumerate(sale.items.all(), 1):
        expiry = add_months(sale_date, item.warranty_months) if item.warranty_months else None
        warranty_label = f'{item.warranty_months} mês(es) - até {expiry:%d/%m/%Y}' if expiry else 'Sem garantia contratual adicional'
        story.append(Paragraph(f'APARELHO {index}', styles['Section']))
        details = Table([
            ['CONDIÇÃO', _value(item.condition_name), 'MARCA', _value(item.brand)],
            ['MODELO', _value(item.model), 'COR', _value(item.color)],
            ['ARMAZENAMENTO', _value(item.storage), 'QUANTIDADE', str(item.quantity)],
            ['IMEI', _value(item.imei), 'NÚMERO DE SÉRIE', _value(item.serial_number)],
            ['SAÚDE DA BATERIA', f'{item.battery_health}%' if item.battery_health is not None else '-', 'GARANTIA CONTRATUAL', warranty_label],
        ], colWidths=[33 * mm, 53 * mm, 39 * mm, 49 * mm])
        details.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), .5, colors.HexColor('#cccccc')), ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f3f3')), ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f3f3f3')), ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 7.7), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
        story.append(details)

    story.extend([Spacer(1, 3 * mm), Paragraph('<b>TERMOS DE GARANTIA</b>', styles['Section'])])
    intro = 'Este termo registra a garantia contratual indicada para cada aparelho, contada da data da venda, sem prejuízo da garantia legal aplicável aos produtos duráveis e dos demais direitos previstos no Código de Defesa do Consumidor.'
    story.append(Paragraph(intro, styles['BodySmall']))
    clauses = [
        '1. A garantia contratual cobre defeitos de fabricação em peças e componentes internos, confirmados mediante análise técnica.',
        '2. A cobertura contempla falhas de funcionamento que não decorram de mau uso, acidente, intervenção indevida ou desgaste natural previamente informado.',
        '3. Recebido o produto para análise, a primeira medida será o reparo do defeito, inclusive com substituição de componentes ou reparo em placa quando tecnicamente indicado.',
        '4. O prazo para saneamento do vício é de até 30 (trinta) dias, ressalvadas as hipóteses legais de solução imediata. Não sendo sanado no prazo aplicável, o consumidor poderá exercer as alternativas previstas no art. 18 do CDC.',
        '5. A garantia contratual é complementar à garantia legal. Para produtos duráveis, o prazo legal para reclamar de vícios aparentes ou de fácil constatação é de 90 (noventa) dias a partir da entrega; para vício oculto, conta-se do momento em que ficar evidenciado.',
        '6. Eventual garantia do fabricante permanece sujeita às condições e ao prazo informados pelo próprio fabricante.',
    ]
    for clause in clauses:
        story.append(Paragraph(clause, styles['BodySmall']))

    story.append(PageBreak())
    story.append(Paragraph('SITUAÇÕES NÃO COBERTAS PELA GARANTIA CONTRATUAL', styles['Section']))
    exclusions = [
        'Danos causados por líquidos, umidade, altas temperaturas, poeira, limalha de metais, quedas, esmagamentos, impactos ou sobrecargas elétricas;',
        'Trincas, quebras, riscos, manchas, descolamentos e danos em telas, lentes, carcaças ou cabos flex decorrentes de ação externa ou mau uso;',
        'Uso de acessórios paralelos, falsificados ou incompatíveis, incluindo carregadores, cabos, fontes, adaptadores e baterias fora das especificações;',
        'Instalação, modificação ou alteração indevida de software, sistema operacional ou componentes;',
        'Abertura do equipamento ou tentativa de reparo por terceiros não autorizados;',
        'Desgaste natural de baterias e peças externas, perda de dados e danos em acessórios não discriminados como itens cobertos.',
    ]
    for exclusion in exclusions:
        story.append(Paragraph(f'• {exclusion}', styles['BodySmall']))
    story.append(Paragraph('<b>IMPORTANTE</b>', styles['Section']))
    story.append(Spacer(1, 1.5 * mm))
    for text in [
        'Produtos seminovos podem apresentar sinais estéticos de uso, os quais devem ser informados no ato da venda.',
        'O produto deverá ser entregue completo para análise técnica, acompanhado do comprovante de compra.',
        'As limitações acima não afastam direitos obrigatórios previstos em lei nem se aplicam quando o problema decorrer de vício do produto.',
    ]:
        story.append(Paragraph(f'• {text}', styles['BodySmall']))

    story.append(Paragraph('DECLARAÇÃO DO CONSUMIDOR', styles['Section']))
    declaration = (
        f'Eu, <b>{sale.customer_name}</b>, declaro ter recebido o(s) produto(s) descrito(s) neste documento nas condições informadas no ato da venda, '
        'com os acessórios discriminados, e estar ciente das condições e limitações da garantia contratual, sem renúncia aos direitos assegurados pela legislação de defesa do consumidor.'
    )
    story.append(Paragraph(declaration, styles['BodySmall']))
    story.append(Spacer(1, 18 * mm))
    signatures = Table([
        ['________________________________________', '________________________________________'],
        [sale.customer_name.upper(), settings.COMPANY_NAME],
        ['CLIENTE', 'FORNECEDOR'],
    ], colWidths=[84 * mm, 84 * mm])
    signatures.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 1), (-1, -1), 4)]))
    story.append(signatures)
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(f'Natal/RN, {sale_date.strftime("%d/%m/%Y")}.', styles['Signature']))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer
