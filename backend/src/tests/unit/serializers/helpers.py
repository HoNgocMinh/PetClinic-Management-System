import pytest
from rest_framework import serializers as drf_serializers


def assert_validation_error(callable_, value):
    with pytest.raises(drf_serializers.ValidationError):
        callable_(value)
