from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from .models import (
    Assessment, Response, Question, DirectiveSection,
    SectionScore, GapReport
)


# ── CONSTANTS ─────────────────────────────────────────────────────────────────

ANSWER_MULTIPLIERS = {
    'yes':        Decimal('1.0'),
    'partial':    Decimal('0.5'),
    'no':         Decimal('0.0'),
    'na':         None,
    'unanswered': Decimal('0.0'),
}

COMPLIANCE_THRESHOLDS = {
    'compliant':     Decimal('80'),
    'partial':       Decimal('60'),
    'at_risk':       Decimal('40'),
    'non_compliant': Decimal('0'),
}


def calculate_response_points(response: Response) -> Decimal:
    multiplier = ANSWER_MULTIPLIERS.get(response.answer)
    if multiplier is None:
        return Decimal('0')
    return (Decimal(str(response.question.max_points)) * multiplier).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )


def get_compliance_rating(percentage: Decimal) -> str:
    if percentage >= COMPLIANCE_THRESHOLDS['compliant']:
        return 'compliant'
    elif percentage >= COMPLIANCE_THRESHOLDS['partial']:
        return 'partial'
    elif percentage >= COMPLIANCE_THRESHOLDS['at_risk']:
        return 'at_risk'
    else:
        return 'non_compliant'


def get_risk_severity(section: DirectiveSection, percentage: Decimal) -> str:
    risk_weights = {
        'critical': 4,
        'high':     3,
        'medium':   2,
        'low':      1,
    }
    compliance_multiplier = (Decimal('100') - percentage) / Decimal('100')
    severity_score = Decimal(str(risk_weights.get(section.risk_level, 1))) * compliance_multiplier

    if severity_score >= Decimal('3'):
        return 'critical'
    elif severity_score >= Decimal('2'):
        return 'high'
    elif severity_score >= Decimal('1'):
        return 'medium'
    else:
        return 'low'


def compute_section_score(assessment: Assessment, section: DirectiveSection) -> dict:
    questions = section.questions.all()
    responses = Response.objects.filter(
        assessment=assessment,
        question__section=section
    ).select_related('question')

    response_map = {r.question_id: r for r in responses}

    raw_score = Decimal('0')
    max_score = Decimal('0')
    gap_count = 0
    partial_count = 0
    na_count = 0

    for question in questions:
        response = response_map.get(question.id)

        if response is None or response.answer == 'unanswered':
            max_score += Decimal(str(question.max_points))
            gap_count += 1
            continue

        if response.answer == 'na':
            na_count += 1
            continue

        max_score += Decimal(str(question.max_points))
        points = calculate_response_points(response)
        raw_score += points

        if response.answer == 'no':
            gap_count += 1
        elif response.answer == 'partial':
            partial_count += 1

    if max_score == Decimal('0'):
        percentage = Decimal('100')
    else:
        percentage = (raw_score / max_score * Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    weighted_score = (percentage * Decimal(str(section.weight)) / Decimal('100')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    return {
        'raw_score': raw_score,
        'max_score': max_score,
        'percentage': percentage,
        'weighted_score': weighted_score,
        'gap_count': gap_count,
        'partial_count': partial_count,
        'na_count': na_count,
        'compliance_rating': get_compliance_rating(percentage),
        'risk_severity': get_risk_severity(section, percentage),
    }


def compute_assessment_score(assessment: Assessment) -> dict:
    sections = DirectiveSection.objects.all().order_by('order')
    section_results = []
    total_weighted_score = Decimal('0')
    total_gaps = 0
    critical_gaps = 0
    high_gaps = 0

    for section in sections:
        score_data = compute_section_score(assessment, section)

        section_score, _ = SectionScore.objects.update_or_create(
            assessment=assessment,
            section=section,
            defaults={
                'raw_score':      score_data['raw_score'],
                'max_score':      score_data['max_score'],
                'percentage':     score_data['percentage'],
                'weighted_score': score_data['weighted_score'],
                'gap_count':      score_data['gap_count'],
                'partial_count':  score_data['partial_count'],
            }
        )

        total_weighted_score += score_data['weighted_score']
        total_gaps += score_data['gap_count']

        if score_data['risk_severity'] in ('critical',) and score_data['gap_count'] > 0:
            critical_gaps += score_data['gap_count']
        elif score_data['risk_severity'] in ('high',) and score_data['gap_count'] > 0:
            high_gaps += score_data['gap_count']

        section_results.append({
            'section': section,
            'score_data': score_data,
            'section_score': section_score,
        })

    overall_percentage = total_weighted_score.quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    overall_score = (overall_percentage * Decimal('10')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    assessment.overall_score = overall_score
    assessment.overall_percentage = overall_percentage
    assessment.save(update_fields=['overall_score', 'overall_percentage'])

    return {
        'assessment': assessment,
        'overall_score': overall_score,
        'overall_percentage': overall_percentage,
        'overall_rating': get_compliance_rating(overall_percentage),
        'total_gaps': total_gaps,
        'critical_gaps': critical_gaps,
        'high_gaps': high_gaps,
        'section_results': section_results,
    }


def get_gap_list(assessment: Assessment) -> list:
    gaps = []
    responses = Response.objects.filter(
        assessment=assessment,
        answer__in=['no', 'partial']
    ).select_related('question', 'question__section').order_by(
        'question__section__order', 'question__order'
    )

    for response in responses:
        section = response.question.section
        gaps.append({
            'question_number': response.question.question_number,
            'question_text': response.question.text,
            'section_number': section.number,
            'section_title': section.title,
            'section_risk_level': section.risk_level,
            'section_weight': section.weight,
            'answer': response.answer,
            'points_lost': Decimal(str(response.question.max_points)) - response.points_awarded,
            'directive_clause': response.question.directive_clause,
            'notes': response.notes,
        })

    gaps.sort(key=lambda g: (
        {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(g['section_risk_level'], 4),
        -g['section_weight'],
        -g['points_lost'],
    ))

    return gaps