from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InstitutionViewSet, DirectiveSectionViewSet, AssessmentViewSet,
    ResponseViewSet, GapReportViewSet, BenchmarkViewSet
)

router = DefaultRouter()
router.register(r'institutions',  InstitutionViewSet,      basename='institution')
router.register(r'sections',      DirectiveSectionViewSet, basename='section')
router.register(r'assessments',   AssessmentViewSet,       basename='assessment')
router.register(r'responses',     ResponseViewSet,         basename='response')
router.register(r'reports',       GapReportViewSet,        basename='report')
router.register(r'benchmarks',    BenchmarkViewSet,        basename='benchmark')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('rest_framework.urls')),
]