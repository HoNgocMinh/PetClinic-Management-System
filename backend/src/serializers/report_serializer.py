from rest_framework import serializers


class ReportDateRangeSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, attrs):
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from phải nhỏ hơn hoặc bằng date_to.")

        return attrs


class RevenueReportQuerySerializer(ReportDateRangeSerializer):
    group_by = serializers.ChoiceField(
        choices=["day", "month"],
        default="day",
        required=False,
    )
