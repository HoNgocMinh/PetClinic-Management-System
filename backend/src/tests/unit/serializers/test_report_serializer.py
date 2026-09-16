import pytest

from src.serializers.report_serializer import (
    ReportDateRangeSerializer,
    RevenueReportQuerySerializer,
)
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_report_date_range_serializer_accepts_valid_range():
    serializer = ReportDateRangeSerializer(
        data={
            "date_from": "2026-05-01",
            "date_to": "2026-05-31",
        },
    )

    assert serializer.is_valid(), serializer.errors


def test_report_date_range_serializer_rejects_invalid_range():
    serializer = ReportDateRangeSerializer()

    assert_validation_error(
        serializer.validate,
        {
            "date_from": "2026-05-31",
            "date_to": "2026-05-01",
        },
    )


def test_revenue_report_query_serializer_defaults_to_day_grouping():
    serializer = RevenueReportQuerySerializer(data={})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["group_by"] == "day"
