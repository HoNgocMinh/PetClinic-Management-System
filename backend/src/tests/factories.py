from datetime import timedelta

import factory
from django.utils import timezone

from src.models import (
    Appointment,
    Clinic,
    MedicalRecord,
    Medicine,
    Pet,
    Payment,
    Prescription,
    PrescriptionItem,
    Service,
    User,
)


class ClinicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Clinic

    name = factory.Sequence(lambda n: f"Clinic {n}")
    address = factory.Sequence(lambda n: f"{n} Test Street")
    phone = "0900000000"
    email = factory.Sequence(lambda n: f"clinic{n}@example.com")
    is_active = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"owner{n}")
    email = factory.Sequence(lambda n: f"owner{n}@example.com")
    full_name = factory.Sequence(lambda n: f"Pet Owner {n}")
    role = User.ROLE_PET_OWNER
    clinic = None
    password = "password123"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "password123")
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, password=password, **kwargs)


class StaffUserFactory(UserFactory):
    username = factory.Sequence(lambda n: f"staff{n}")
    email = factory.Sequence(lambda n: f"staff{n}@example.com")
    full_name = factory.Sequence(lambda n: f"Clinic Staff {n}")
    role = User.ROLE_CLINIC_STAFF
    clinic = factory.SubFactory(ClinicFactory)


class AdminUserFactory(UserFactory):
    username = factory.Sequence(lambda n: f"admin{n}")
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    full_name = factory.Sequence(lambda n: f"Admin User {n}")
    role = User.ROLE_ADMIN


class PetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pet

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Pet {n}")
    species = Pet.SPECIES_DOG
    breed = "Poodle"
    gender = Pet.GENDER_MALE
    birth_date = None
    weight = "4.50"
    note = ""
    is_active = True


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    clinic = factory.SubFactory(ClinicFactory)
    name = factory.Sequence(lambda n: f"Service {n}")
    service_type = Service.SERVICE_EXAM
    description = "Regular checkup"
    price = "100000.00"
    duration_minutes = 60
    is_active = True


class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appointment

    owner = factory.SubFactory(UserFactory)
    pet = factory.SubFactory(PetFactory, owner=factory.SelfAttribute("..owner"))
    clinic = factory.SubFactory(ClinicFactory)
    service = factory.SubFactory(ServiceFactory, clinic=factory.SelfAttribute("..clinic"))
    appointment_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    note = ""
    status = Appointment.STATUS_PENDING


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    appointment = factory.SubFactory(AppointmentFactory, status=Appointment.STATUS_COMPLETED)
    owner = factory.LazyAttribute(lambda payment: payment.appointment.owner)
    clinic = factory.LazyAttribute(lambda payment: payment.appointment.clinic)
    amount = "100000.00"
    method = Payment.METHOD_VNPAY
    status = Payment.STATUS_PENDING
    paid_at = None
    transaction_code = None
    note = ""


class MedicineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Medicine

    clinic = factory.SubFactory(ClinicFactory)
    name = factory.Sequence(lambda n: f"Medicine {n}")
    unit = "tablet"
    description = "Test medicine"
    stock_quantity = 10
    price = "5000.00"
    is_active = True


class MedicalRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MedicalRecord

    appointment = factory.SubFactory(AppointmentFactory, status=Appointment.STATUS_COMPLETED)
    pet = factory.LazyAttribute(lambda record: record.appointment.pet)
    clinic = factory.LazyAttribute(lambda record: record.appointment.clinic)
    staff = factory.SubFactory(StaffUserFactory, clinic=factory.SelfAttribute("..clinic"))
    symptoms = "Coughing"
    diagnosis = "Mild respiratory infection"
    treatment = "Rest and medication"
    note = ""


class PrescriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Prescription

    medical_record = factory.SubFactory(MedicalRecordFactory)
    clinic = factory.LazyAttribute(lambda prescription: prescription.medical_record.clinic)
    staff = factory.LazyAttribute(lambda prescription: prescription.medical_record.staff)
    note = "Take medicine after meals"


class PrescriptionItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PrescriptionItem

    prescription = factory.SubFactory(PrescriptionFactory)
    medicine = factory.LazyAttribute(
        lambda item: MedicineFactory(clinic=item.prescription.clinic),
    )
    quantity = 2
    dosage = "1 tablet"
    frequency = "Twice daily"
    duration_days = 5
    instruction = "After meal"
