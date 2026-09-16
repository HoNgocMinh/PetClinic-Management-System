from src.common.base_model import TimeStampedModel
from src.tests.factories import ClinicFactory


def test_timestamped_model_is_abstract_and_defines_timestamp_fields():
    assert TimeStampedModel._meta.abstract is True
    assert TimeStampedModel._meta.get_field("created_at").auto_now_add is True
    assert TimeStampedModel._meta.get_field("updated_at").auto_now is True


def test_timestamped_model_fields_are_populated_on_concrete_models(db):
    clinic = ClinicFactory()

    assert clinic.created_at is not None
    assert clinic.updated_at is not None
