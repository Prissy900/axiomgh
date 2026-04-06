from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


# ── INSTITUTION ────────────────────────────────────────────────────────────────

class Institution(models.Model):
    INSTITUTION_TYPES = [
        ('commercial_bank', 'Commercial Bank'),
        ('savings_bank', 'Savings & Loans'),
        ('rural_bank', 'Rural/Community Bank'),
        ('fintech', 'Fintech Company'),
        ('payment_processor', 'Payment System Operator'),
        ('insurance', 'Insurance Company'),
        ('microfinance', 'Microfinance Institution'),
        ('other', 'Other Regulated Entity'),
    ]

    TIER_CHOICES = [
        ('single', 'Single Institution'),
        ('multi_branch', 'Multi-Branch Group'),
        ('holding', 'Financial Group / Holding'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    institution_type = models.CharField(max_length=50, choices=INSTITUTION_TYPES)
    license_number = models.CharField(max_length=100, unique=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='single')
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ── USER ───────────────────────────────────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('ciso', 'CISO'),
        ('compliance_officer', 'Compliance Officer'),
        ('board', 'Board Member'),
        ('it_manager', 'IT Manager'),
        ('admin', 'Platform Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name='users', null=True, blank=True
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='compliance_officer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ── DIRECTIVE SECTION ──────────────────────────────────────────────────────────

class DirectiveSection(models.Model):
    RISK_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=5)           # e.g. "01", "08"
    title = models.CharField(max_length=255)
    description = models.TextField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 10.00 = 10%
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    directive_reference = models.CharField(max_length=100, blank=True)  # e.g. "Part II, Sections 4-6"
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Section {self.number}: {self.title}"


# ── QUESTION ───────────────────────────────────────────────────────────────────

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(
        DirectiveSection, on_delete=models.CASCADE, related_name='questions'
    )
    question_number = models.CharField(max_length=10)   # e.g. "1.1", "8.3"
    text = models.TextField()
    max_points = models.PositiveIntegerField(default=10)
    directive_clause = models.CharField(max_length=100, blank=True)  # e.g. "Section 4(3)"
    guidance_note = models.TextField(blank=True)        # Examiner guidance shown in platform
    requires_evidence = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['section__order', 'order']

    def __str__(self):
        return f"Q{self.question_number}: {self.text[:60]}..."


# ── ASSESSMENT ─────────────────────────────────────────────────────────────────

class Assessment(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('report_generated', 'Report Generated'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name='assessments'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='assessments_created'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    overall_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )                                                   # out of 1000
    overall_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.institution.name} — Assessment {self.started_at.strftime('%Y-%m-%d')}"

    @property
    def completion_percentage(self):
        total_questions = Question.objects.count()
        answered = self.responses.exclude(answer='unanswered').count()
        if total_questions == 0:
            return 0
        return round((answered / total_questions) * 100, 1)


# ── RESPONSE ───────────────────────────────────────────────────────────────────

class Response(models.Model):
    ANSWER_CHOICES = [
        ('yes', 'Yes — Fully Compliant'),
        ('partial', 'Partial — Partially Compliant'),
        ('no', 'No — Not Compliant'),
        ('na', 'N/A — Not Applicable'),
        ('unanswered', 'Not Yet Answered'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='responses'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='responses'
    )
    answer = models.CharField(max_length=20, choices=ANSWER_CHOICES, default='unanswered')
    points_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)               # Compliance officer notes
    answered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assessment', 'question')
        ordering = ['question__section__order', 'question__order']

    def __str__(self):
        return f"{self.assessment} — Q{self.question.question_number}: {self.answer}"

    def calculate_points(self):
        """Auto-calculate points based on answer and question max_points."""
        if self.answer == 'yes':
            return self.question.max_points
        elif self.answer == 'partial':
            return self.question.max_points * 0.5
        else:
            return 0

    def save(self, *args, **kwargs):
        self.points_awarded = self.calculate_points()
        super().save(*args, **kwargs)


# ── EVIDENCE ───────────────────────────────────────────────────────────────────

class Evidence(models.Model):
    FILE_TYPES = [
        ('policy', 'Policy Document'),
        ('certificate', 'Certificate'),
        ('audit_report', 'Audit Report'),
        ('screenshot', 'Screenshot'),
        ('procedure', 'Procedure Document'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(
        Response, on_delete=models.CASCADE, related_name='evidence_files'
    )
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()                       # S3 URL
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='other')
    file_size_kb = models.PositiveIntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)  # For certificates
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} — {self.response.question.question_number}"


# ── SECTION SCORE ──────────────────────────────────────────────────────────────

class SectionScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='section_scores'
    )
    section = models.ForeignKey(
        DirectiveSection, on_delete=models.CASCADE, related_name='scores'
    )
    raw_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    weighted_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    gap_count = models.PositiveIntegerField(default=0)  # Number of No answers
    partial_count = models.PositiveIntegerField(default=0)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assessment', 'section')

    def __str__(self):
        return f"{self.assessment.institution.name} — {self.section.title}: {self.percentage}%"

    @property
    def risk_rating(self):
        if self.percentage >= 80:
            return 'compliant'
        elif self.percentage >= 60:
            return 'partial'
        elif self.percentage >= 40:
            return 'at_risk'
        else:
            return 'non_compliant'


# ── GAP REPORT ─────────────────────────────────────────────────────────────────

class GapReport(models.Model):
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.OneToOneField(
        Assessment, on_delete=models.CASCADE, related_name='gap_report'
    )
    pdf_url = models.URLField(blank=True)              # S3 URL for generated PDF
    overall_score = models.DecimalField(max_digits=6, decimal_places=2)
    overall_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_gaps = models.PositiveIntegerField(default=0)
    critical_gaps = models.PositiveIntegerField(default=0)
    high_gaps = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    report_version = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Gap Report — {self.assessment.institution.name} ({self.generated_at.strftime('%Y-%m-%d')})"


# ── BENCHMARK ──────────────────────────────────────────────────────────────────

class Benchmark(models.Model):
    """
    Anonymised aggregate scores per institution type per section.
    Updated periodically from completed assessments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution_type = models.CharField(max_length=50)
    section = models.ForeignKey(
        DirectiveSection, on_delete=models.CASCADE, related_name='benchmarks'
    )
    avg_score = models.DecimalField(max_digits=5, decimal_places=2)
    median_score = models.DecimalField(max_digits=5, decimal_places=2)
    top_quartile_score = models.DecimalField(max_digits=5, decimal_places=2)
    sample_size = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('institution_type', 'section')

    def __str__(self):
        return f"Benchmark: {self.institution_type} — {self.section.title}"


# ── AUDIT LOG ──────────────────────────────────────────────────────────────────

class AuditLog(models.Model):
    """
    Immutable log of all significant platform actions.
    Used for compliance and security tracking.
    """
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('assessment_started', 'Assessment Started'),
        ('response_saved', 'Response Saved'),
        ('evidence_uploaded', 'Evidence Uploaded'),
        ('report_generated', 'Report Generated'),
        ('report_downloaded', 'Report Downloaded'),
        ('user_created', 'User Created'),
        ('license_issued', 'License Issued'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    detail = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} — {self.user} at {self.timestamp}"