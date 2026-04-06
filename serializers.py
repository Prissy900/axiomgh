from rest_framework import serializers
from django.utils import timezone
from .models import (
    Institution, User, Assessment, Response, Evidence,
    DirectiveSection, Question, SectionScore, GapReport, Benchmark
)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'institution_type', 'license_number',
            'tier', 'address', 'website', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'institution', 'institution_name', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}


class DirectiveSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectiveSection
        fields = [
            'id', 'number', 'title', 'description',
            'weight', 'risk_level', 'directive_reference', 'order'
        ]


class QuestionSerializer(serializers.ModelSerializer):
    section_title = serializers.CharField(source='section.title', read_only=True)
    section_number = serializers.CharField(source='section.number', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_number', 'text', 'max_points',
            'directive_clause', 'guidance_note', 'requires_evidence',
            'order', 'section', 'section_title', 'section_number'
        ]


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = [
            'id', 'file_name', 'file_url', 'file_type',
            'file_size_kb', 'uploaded_at', 'expiry_date', 'is_verified'
        ]
        read_only_fields = ['id', 'uploaded_at']


class ResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_number = serializers.CharField(source='question.question_number', read_only=True)
    max_points = serializers.IntegerField(source='question.max_points', read_only=True)
    evidence_files = EvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = Response
        fields = [
            'id', 'question', 'question_text', 'question_number',
            'answer', 'points_awarded', 'notes', 'answered_at',
            'max_points', 'evidence_files'
        ]
        read_only_fields = ['id', 'points_awarded', 'answered_at']

    def update(self, instance, validated_data):
        if 'answer' in validated_data and validated_data['answer'] != 'unanswered':
            validated_data['answered_at'] = timezone.now()
        return super().update(instance, validated_data)


class SectionScoreSerializer(serializers.ModelSerializer):
    section_title = serializers.CharField(source='section.title', read_only=True)
    section_number = serializers.CharField(source='section.number', read_only=True)
    section_risk_level = serializers.CharField(source='section.risk_level', read_only=True)
    compliance_rating = serializers.SerializerMethodField()

    class Meta:
        model = SectionScore
        fields = [
            'id', 'section', 'section_title', 'section_number',
            'section_risk_level', 'raw_score', 'max_score',
            'percentage', 'weighted_score', 'gap_count',
            'partial_count', 'compliance_rating', 'computed_at'
        ]

    def get_compliance_rating(self, obj):
        return obj.risk_rating


class AssessmentSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    section_scores = SectionScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'institution', 'institution_name', 'status',
            'overall_score', 'overall_percentage', 'started_at',
            'completed_at', 'notes', 'section_scores'
        ]
        read_only_fields = [
            'id', 'institution', 'overall_score', 'overall_percentage',
            'started_at', 'completed_at'
        ]


class GapReportSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(
        source='assessment.institution.name', read_only=True
    )

    class Meta:
        model = GapReport
        fields = [
            'id', 'assessment', 'institution_name', 'pdf_url',
            'overall_score', 'overall_percentage', 'total_gaps',
            'critical_gaps', 'high_gaps', 'status',
            'generated_at', 'report_version'
        ]
        read_only_fields = ['id', 'generated_at']


class BenchmarkSerializer(serializers.ModelSerializer):
    section_title = serializers.CharField(source='section.title', read_only=True)

    class Meta:
        model = Benchmark
        fields = [
            'id', 'institution_type', 'section', 'section_title',
            'avg_score', 'median_score', 'top_quartile_score',
            'sample_size', 'last_updated'
        ]
