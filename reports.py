from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
import io

from .models import Assessment, SectionScore
from .scoring import get_gap_list
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

DARK  = colors.HexColor('#080C12')
DARK2 = colors.HexColor('#0D1520')
DARK3 = colors.HexColor('#111D2E')
GOLD  = colors.HexColor('#F0B429')
TEXT  = colors.HexColor('#E8EEF5')
TEXT2 = colors.HexColor('#8FA4BF')
TEXT3 = colors.HexColor('#4A6480')
RED   = colors.HexColor('#E53E3E')
ORANGE= colors.HexColor('#DD6B20')
GREEN = colors.HexColor('#38A169')
YELLOW= colors.HexColor('#D69E2E')
BORDER= colors.HexColor('#1E2D42')


def rc(pct):
    pct = float(pct)
    if pct >= 80: return GREEN
    if pct >= 60: return YELLOW
    if pct >= 40: return ORANGE
    return RED

def rl(pct):
    pct = float(pct)
    if pct >= 80: return 'COMPLIANT'
    if pct >= 60: return 'PARTIAL'
    if pct >= 40: return 'AT RISK'
    return 'NON-COMPLIANT'

def riskc(risk):
    return {'critical': RED, 'high': ORANGE, 'medium': YELLOW, 'low': GREEN}.get(risk, TEXT2)


def generate_pdf_report(assessment):
    institution = assessment.institution
    scores = SectionScore.objects.filter(assessment=assessment).select_related('section').order_by('section__order')
    gaps = get_gap_list(assessment)

    overall_pct = float(assessment.overall_percentage or 0)
    overall_score = float(assessment.overall_score or 0)
    r_color = rc(overall_pct)
    r_label = rl(overall_pct)
    total_gaps = len([g for g in gaps if g['answer'] == 'no'])
    partial_gaps = len([g for g in gaps if g['answer'] == 'partial'])
    critical_gaps = len([g for g in gaps if g['section_risk_level'] == 'critical' and g['answer'] == 'no'])
    date_str = timezone.now().strftime("%d %B %Y")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []

    def p(text, size=10, color=TEXT2, bold=False, align=TA_LEFT):
        weight = 'Helvetica-Bold' if bold else 'Helvetica'
        return Paragraph(f'<font name="{weight}" size="{size}" color="{color.hexval()}">{text}</font>',
            ParagraphStyle('x', fontName=weight, fontSize=size, textColor=color,
                           alignment=align, leading=size*1.4))

    def mono(text, size=9, color=TEXT3):
        return Paragraph(f'<font name="Courier" size="{size}" color="{color.hexval()}">{text}</font>',
            ParagraphStyle('m', fontName='Courier', fontSize=size, textColor=color, leading=size*1.4))

    def bg_table(content, bg=DARK2, pad=14):
        return Table([[content]], colWidths=[170*mm],
            style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), bg),
                ('TOPPADDING', (0,0), (-1,-1), pad//2),
                ('BOTTOMPADDING', (0,0), (-1,-1), pad//2),
                ('LEFTPADDING', (0,0), (-1,-1), pad),
                ('RIGHTPADDING', (0,0), (-1,-1), pad),
            ]))

    # ── COVER ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 6*mm))
    story.append(bg_table(p('AxiomGH  —  CISD 2026 Compliance Intelligence', 14, GOLD, True), DARK2, 16))
    story.append(Spacer(1, 6*mm))
    story.append(p('COMPLIANCE ASSESSMENT REPORT', 8, TEXT3))
    story.append(Spacer(1, 2*mm))
    story.append(p(institution.name, 24, TEXT, True))
    story.append(Spacer(1, 2*mm))
    story.append(p('Bank of Ghana Cyber and Information Security Directive 2026', 12, TEXT2))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER, spaceAfter=6*mm, spaceBefore=6*mm))

    # Score cards
    story.append(Table([[
        p(f'{overall_score:.0f}', 40, r_color, True, TA_CENTER),
        Table([
            [p('Critical Gaps', 8, TEXT3, False, TA_CENTER)],
            [p(str(critical_gaps), 22, RED, True, TA_CENTER)],
        ], colWidths=[35*mm], style=TableStyle([('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)])),
        Table([
            [p('Non-Compliant', 8, TEXT3, False, TA_CENTER)],
            [p(str(total_gaps), 22, ORANGE, True, TA_CENTER)],
        ], colWidths=[35*mm], style=TableStyle([('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)])),
        Table([
            [p('Partial', 8, TEXT3, False, TA_CENTER)],
            [p(str(partial_gaps), 22, YELLOW, True, TA_CENTER)],
        ], colWidths=[35*mm], style=TableStyle([('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)])),
        Table([
            [p('Compliance', 8, TEXT3, False, TA_CENTER)],
            [p(f'{overall_pct:.1f}%', 22, r_color, True, TA_CENTER)],
        ], colWidths=[35*mm], style=TableStyle([('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)])),
    ]], colWidths=[30*mm, 35*mm, 35*mm, 35*mm, 35*mm],
    style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK2),
        ('TOPPADDING', (0,0), (-1,-1), 14), ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 10), ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEAFTER', (0,0), (3,0), 0.5, BORDER),
    ])))
    story.append(Spacer(1, 4*mm))
    story.append(bg_table(p(f'OVERALL RATING: {r_label}', 11, r_color, True), DARK2, 12))
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Table([[
        p(f'Generated: {date_str}', 8, TEXT3),
        p('CONFIDENTIAL — FOR BOARD AND REGULATORY USE ONLY', 8, TEXT3, False, TA_RIGHT),
    ]], colWidths=[85*mm, 85*mm], style=TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0)
    ])))

    story.append(PageBreak())

    # ── SECTION SCORES ────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=3, color=GOLD, spaceAfter=5*mm))
    story.append(p('SECTION 01', 8, TEXT3))
    story.append(p('Section Compliance Scores', 18, TEXT, True))
    story.append(p('Compliance across all 23 CISD 2026 directive sections', 10, TEXT2))
    story.append(Spacer(1, 4*mm))

    rows = [[
        p('#', 8, TEXT3, True), p('SECTION', 8, TEXT3, True), p('RISK', 8, TEXT3, True),
        p('SCORE', 8, TEXT3, True), p('%', 8, TEXT3, True), p('GAPS', 8, TEXT3, True),
    ]]
    for sc in scores:
        pct = float(sc.percentage)
        rows.append([
            mono(sc.section.number, 8, TEXT3),
            p(sc.section.title, 8, TEXT),
            p(sc.section.risk_level.upper(), 8, riskc(sc.section.risk_level), True),
            p('█' * int(pct/10) + '░' * (10 - int(pct/10)), 8, rc(pct)),
            p(f'{pct:.0f}%', 8, rc(pct), True),
            p(str(sc.gap_count) if sc.gap_count > 0 else '—', 8, RED if sc.gap_count > 0 else TEXT3),
        ])

    t = Table(rows, colWidths=[13*mm, 68*mm, 20*mm, 28*mm, 14*mm, 14*mm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [DARK2, DARK]),
        ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 7), ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, BORDER),
    ]))
    story.append(t)
    story.append(Spacer(1, 5*mm))
    story.append(bg_table(p('SCORING: Yes = Full pts | Partial = 50% | No = 0 | N/A = Excluded. '
                            'Compliant ≥80% | Partial 60-79% | At Risk 40-59% | Non-Compliant <40%', 8, TEXT2), DARK2, 12))

    story.append(PageBreak())

    # ── GAP REPORT ────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=3, color=GOLD, spaceAfter=5*mm))
    story.append(p('SECTION 02', 8, TEXT3))
    story.append(p('Priority Gap Report', 18, TEXT, True))
    story.append(p(f'{len(gaps)} gaps identified — sorted by risk severity', 10, TEXT2))
    story.append(Spacer(1, 4*mm))

    if not gaps:
        story.append(bg_table(p('No gaps identified — Fully Compliant', 12, GREEN, True), DARK2, 20))
    else:
        grows = [[
            p('REF', 8, TEXT3, True), p('QUESTION', 8, TEXT3, True),
            p('RISK', 8, TEXT3, True), p('STATUS', 8, TEXT3, True), p('PTS LOST', 8, TEXT3, True),
        ]]
        for gap in gaps[:60]:
            sc = RED if gap['answer'] == 'no' else YELLOW
            grows.append([
                mono(f'{gap["section_number"]}.{gap["question_number"]}', 7, TEXT3),
                p(gap['question_text'][:120] + ('...' if len(gap['question_text']) > 120 else ''), 7, TEXT),
                p(gap['section_risk_level'].upper(), 7, riskc(gap['section_risk_level']), True),
                p('No' if gap['answer'] == 'no' else 'Partial', 7, sc, True),
                p(f'-{float(gap["points_lost"]):.0f}', 7, RED),
            ])

        gt = Table(grows, colWidths=[18*mm, 88*mm, 20*mm, 22*mm, 18*mm], repeatRows=1)
        gt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), DARK3),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [DARK2, DARK]),
            ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, BORDER),
        ]))
        story.append(gt)

    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Table([[
        p('AxiomGH — CISD 2026 Compliance Intelligence', 8, TEXT3),
        p(f'{institution.name} | {date_str} | CONFIDENTIAL', 8, TEXT3, False, TA_RIGHT),
    ]], colWidths=[85*mm, 85*mm], style=TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)
    ])))

    # ── BUILD ─────────────────────────────────────────────────────────────────
    def dark_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(DARK)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=dark_bg, onLaterPages=dark_bg)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    fname = f"AxiomGH_CISD2026_{institution.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response
