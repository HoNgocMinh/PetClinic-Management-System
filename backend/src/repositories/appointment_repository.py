from src.models import Appointment


class AppointmentRepository:
    APPOINTMENT_SELECT_RELATED = ("owner", "pet", "clinic", "service", "medical_record", "payment")

    @staticmethod
    def create(**kwargs):
        return Appointment.objects.create(**kwargs)

    @staticmethod
    def get_all_by_owner(owner):
        return Appointment.objects.select_related(
            *AppointmentRepository.APPOINTMENT_SELECT_RELATED
        ).filter(owner=owner).order_by("-created_at")

    @staticmethod
    def get_all_by_clinic_id(clinic_id: int):
        return Appointment.objects.select_related(
            *AppointmentRepository.APPOINTMENT_SELECT_RELATED
        ).filter(clinic_id=clinic_id).order_by("-appointment_time", "-created_at")

    @staticmethod
    def get_active_by_clinic_id(clinic_id: int):
        return Appointment.objects.select_related(
            *AppointmentRepository.APPOINTMENT_SELECT_RELATED
        ).filter(
            clinic_id=clinic_id,
            status__in=[
                Appointment.STATUS_PENDING,
                Appointment.STATUS_CONFIRMED,
                Appointment.STATUS_CHECKED_IN,
                Appointment.STATUS_IN_PROGRESS,
            ],
        ).order_by("appointment_time", "-created_at")

    @staticmethod
    def get_by_id(appointment_id: int):
        return Appointment.objects.select_related(
            *AppointmentRepository.APPOINTMENT_SELECT_RELATED
        ).filter(id=appointment_id).first()

    @staticmethod
    def save(appointment: Appointment):
        appointment.save()
        return appointment

    @staticmethod
    def delete(appointment: Appointment):
        appointment.delete()
