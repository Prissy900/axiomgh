from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import (
    Institution, Assessment, Response, Evidence,
    DirectiveSection, Question, SectionScore, GapReport, Benchmark
)
from .serializers import (
    InstitutionSerializer, AssessmentSerializer, ResponseSerializer,
    EvidenceSerializer, DirectiveSectionSerializer, QuestionSerializer,
    SectionScoreSerializer, GapReportSerializer, BenchmarkSerializer
)
from .scoring import compute_assessment_score, get_gap_list
from .reports import generate_pdf_report


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.filter(is_active=True)
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Institution.objects.all()
        return Institution.objects.filter(id=user.institution_id)


class DirectiveSectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DirectiveSection.objects.all().order_by('order')
    serializer_class = DirectiveSectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        section = self.get_object()
        questions = section.questions.all().order_by('order')
        serializer = QuestionSerializer(questions, many=True)
        return DRFResponse(serializer.data)


class AssessmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Assessment.objects.all().select_related('institution')
        return Assessment.objects.filter(
            institution=user.institution
        ).select_related('institution')

    def perform_create(self, serializer):
        serializer.save(
            institution=self.request.user.institution,
            status='in_progress'
        )

    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        assessment = self.get_object()
        sections = DirectiveSection.objects.all().order_by('order')
        result = []

        for section in sections:
            questions = section.questions.all().order_by('order')
            section_responses = []

            for question in questions:
                response, created = Response.objects.get_or_create(
                    assessment=assessment,
                    question=question,
                    defaults={'answer': 'unanswered'}
                )
                section_responses.append(ResponseSerializer(response).data)

            result.append({
                'section_id': str(section.id),
                'section_number': section.number,
                'section_title': section.title,
                'section_risk_level': section.risk_level,
                'section_weight': str(section.weight),
                'responses': section_responses,
            })

        return DRFResponse(result)

    @action(detail=True, methods=['post'])
    def compute_score(self, request, pk=None):
        assessment = self.get_object()
        with transaction.atomic():
            score_data = compute_assessment_score(assessment)
        return DRFResponse({
            'overall_score': str(score_data['overall_score']),
            'overall_percentage': str(score_data['overall_percentage']),
            'overall_rating': score_data['overall_rating'],
            'total_gaps': score_data['total_gaps'],
            'critical_gaps': score_data['critical_gaps'],
            'high_gaps': score_data['high_gaps'],
            'section_count': len(score_data['section_results']),
        })

    @action(detail=True, methods=['get'])
    def scores(self, request, pk=None):
        assessment = self.get_object()
        section_scores = SectionScore.objects.filter(
            assessment=assessment
        ).select_related('section').order_by('section__order')
        serializer = SectionScoreSerializer(section_scores, many=True)
        return DRFResponse(serializer.data)

    @action(detail=True, methods=['get'])
    def gaps(self, request, pk=None):
        assessment = self.get_object()
        gaps = get_gap_list(assessment)
        return DRFResponse(gaps)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        assessment = self.get_object()
        if assessment.status == 'completed':
            return DRFResponse(
                {'error': 'Assessment already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            score_data = compute_assessment_score(assessment)
            assessment.status = 'completed'
            assessment.completed_at = timezone.now()
            assessment.save(update_fields=['status', 'completed_at'])
        return DRFResponse({
            'message': 'Assessment completed successfully.',
            'overall_score': str(score_data['overall_score']),
            'overall_percentage': str(score_data['overall_percentage']),
            'overall_rating': score_data['overall_rating'],
            'total_gaps': score_data['total_gaps'],
        })

    @action(detail=True, methods=['get'])
    def benchmark(self, request, pk=None):
        assessment = self.get_object()
        institution_type = assessment.institution.institution_type
        section_scores = SectionScore.objects.filter(
            assessment=assessment
        ).select_related('section')
        benchmarks = Benchmark.objects.filter(
            institution_type=institution_type
        ).select_related('section')
        benchmark_map = {b.section_id: b for b in benchmarks}
        result = []
        for score in section_scores:
            bench = benchmark_map.get(score.section_id)
            result.append({
                'section_number': score.section.number,
                'section_title': score.section.title,
                'your_score': str(score.percentage),
                'peer_average': str(bench.avg_score) if bench else None,
                'peer_median': str(bench.median_score) if bench else None,
                'peer_top_quartile': str(bench.top_quartile_score) if bench else None,
                'vs_average': str(score.percentage - bench.avg_score) if bench else None,
            })
        return DRFResponse(result)

    @action(detail=True, methods=['get'])
    def pdf_report(self, request, pk=None):
        assessment = self.get_object()
        if assessment.status != 'completed':
            return DRFResponse(
                {'error': 'Assessment must be completed before generating a report.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return generate_pdf_report(assessment)


class ResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Response.objects.filter(
            assessment__institution=self.request.user.institution
        ).select_related('question', 'question__section')

    def perform_update(self, serializer):
        serializer.save(answered_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_save(self, request):
        assessment_id = request.data.get('assessment_id')
        responses_data = request.data.get('responses', [])

        assessment = get_object_or_404(
            Assessment,
            id=assessment_id,
            institution=request.user.institution
        )

        saved = []
        errors = []

        with transaction.atomic():
            for item in responses_data:
                try:
                    response = Response.objects.get(
                        assessment=assessment,
                        question_id=item['question_id']
                    )
                    response.answer = item.get('answer', response.answer)
                    response.notes = item.get('notes', response.notes)
                    response.answered_by = request.user
                    if response.answer != 'unanswered':
                        response.answered_at = timezone.now()
                    response.save()
                    saved.append(str(response.id))
                except Response.DoesNotExist:
                    errors.append({
                        'question_id': item.get('question_id'),
                        'error': 'Response not found'
                    })
                except Exception as e:
                    errors.append({
                        'question_id': item.get('question_id'),
                        'error': str(e)
                    })

        return DRFResponse({
            'saved_count': len(saved),
            'error_count': len(errors),
            'errors': errors,
        })


class GapReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GapReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GapReport.objects.filter(
            assessment__institution=self.request.user.institution
        ).select_related('assessment', 'assessment__institution')


class BenchmarkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BenchmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        institution_type = self.request.query_params.get('type')
        qs = Benchmark.objects.select_related('section')
        if institution_type:
            qs = qs.filter(institution_type=institution_type)
        return qs
