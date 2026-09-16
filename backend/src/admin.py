from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

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
    StaffUser,
    User,
)

admin.site.site_header = "Trang quản trị hệ thống thú y"
admin.site.site_title = "Quản trị thú y"
admin.site.index_title = "Quản lý dữ liệu"


class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        clinic = cleaned_data.get("clinic")

        if role == User.ROLE_CLINIC_STAFF and not clinic:
            raise ValidationError("Nhân viên phòng khám bắt buộc phải thuộc một phòng khám.")

        if role in [User.ROLE_PET_OWNER, User.ROLE_ADMIN] and clinic is not None:
            raise ValidationError("Chỉ nhân viên phòng khám mới được phép thuộc một phòng khám.")

        return cleaned_data


class StaffAdminForm(forms.ModelForm):
    class Meta:
        model = StaffUser
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        self.instance.role = User.ROLE_CLINIC_STAFF
        self.instance.is_staff = False
        self.instance.is_superuser = False
        clinic = cleaned_data.get("clinic")
        if not clinic:
            raise ValidationError("Nhân viên phòng khám bắt buộc phải thuộc một phòng khám.")
        return cleaned_data


class StaffUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, label="Họ và tên")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, required=False, label="Số điện thoại")
    address = forms.CharField(widget=forms.Textarea, required=False, label="Địa chỉ")
    clinic = forms.ModelChoiceField(queryset=Clinic.objects.all(), label="Phòng khám")
    is_active = forms.BooleanField(required=False, initial=True, label="Đang hoạt động")

    class Meta(UserCreationForm.Meta):
        model = StaffUser
        fields = ("username", "full_name", "email", "phone", "address", "clinic", "is_active")

    def clean(self):
        cleaned_data = super().clean()
        self.instance.role = User.ROLE_CLINIC_STAFF
        self.instance.is_staff = False
        self.instance.is_superuser = False
        clinic = cleaned_data.get("clinic")
        if not clinic:
            raise ValidationError("Nhân viên phòng khám bắt buộc phải thuộc một phòng khám.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_CLINIC_STAFF
        user.is_staff = False
        user.is_superuser = False
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.clinic = self.cleaned_data["clinic"]
        user.is_active = self.cleaned_data.get("is_active", True)
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserAdminForm

    list_display = (
        "id",
        "username",
        "email",
        "full_name",
        "role",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = ("role", "is_active")
    search_fields = ("username", "email", "full_name", "phone")
    ordering = ("-id",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Thông tin bổ sung", {"fields": ("full_name", "phone", "address", "role")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Thông tin bổ sung", {"fields": ("full_name", "email", "phone", "address", "role")}),
    )

    def save_model(self, request, obj, form, change):
        if obj.role == User.ROLE_ADMIN:
            obj.is_staff = True
            obj.is_superuser = True
        else:
            obj.is_staff = False
            obj.is_superuser = False

        super().save_model(request, obj, form, change)


@admin.register(StaffUser)
class StaffUserAdmin(BaseUserAdmin):
    form = StaffAdminForm
    add_form = StaffUserCreationForm

    list_display = (
        "id",
        "username",
        "email",
        "full_name",
        "clinic",
        "is_active",
        "created_at",
    )
    list_filter = ("clinic", "is_active")
    search_fields = ("username", "email", "full_name", "phone")
    ordering = ("-id",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin cá nhân", {"fields": ("first_name", "last_name", "full_name", "email", "phone", "address")}),
        ("Thông tin nhân viên", {"fields": ("clinic", "is_active")}),
        ("Quyền hạn", {"fields": ("groups", "user_permissions")}),
        ("Mốc thời gian", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "full_name",
                    "email",
                    "phone",
                    "address",
                    "clinic",
                    "is_active",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(role=User.ROLE_CLINIC_STAFF)

    def save_model(self, request, obj, form, change):
        obj.role = User.ROLE_CLINIC_STAFF
        obj.is_staff = False
        obj.is_superuser = False
        super().save_model(request, obj, form, change)


class SoftDeleteAdminMixin:
    actions = None

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])

    def delete_queryset(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Clinic)
class ClinicAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "is_active", "created_at")
    search_fields = ("name", "phone", "email")
    list_filter = ("is_active",)


@admin.register(Pet)
class PetAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "species", "breed", "owner", "is_active", "created_at")
    search_fields = ("name", "species", "breed", "owner__username", "owner__full_name")
    list_filter = ("species", "is_active")


@admin.register(Service)
class ServiceAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "clinic",
        "formatted_price",
        "duration_minutes",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "clinic__name")
    list_filter = ("clinic", "is_active")

    @admin.display(description="Giá")
    def formatted_price(self, obj):
        return f"{obj.price:,.0f} VNĐ".replace(",", ".")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "clinic", "service", "appointment_time", "status", "created_at")
    search_fields = ("pet__name", "clinic__name", "service__name")
    list_filter = ("status", "clinic", "appointment_time")
    readonly_fields = (
        "owner",
        "pet",
        "clinic",
        "service",
        "appointment_time",
        "note",
        "status",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "pet", "clinic", "staff", "created_at")
    search_fields = (
        "appointment__id",
        "pet__name",
        "clinic__name",
        "staff__username",
        "staff__full_name",
    )
    list_filter = ("clinic", "staff", "created_at")
    readonly_fields = (
        "appointment",
        "pet",
        "clinic",
        "staff",
        "symptoms",
        "diagnosis",
        "treatment",
        "note",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Medicine)
class MedicineAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "clinic",
        "unit",
        "stock_quantity",
        "formatted_price",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "clinic__name", "unit")
    list_filter = ("clinic", "is_active")

    @admin.display(description="Giá")
    def formatted_price(self, obj):
        return f"{obj.price:,.0f} VNĐ".replace(",", ".")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    class PrescriptionItemInline(admin.TabularInline):
        model = PrescriptionItem
        extra = 0
        can_delete = False
        readonly_fields = (
            "medicine",
            "quantity",
            "dosage",
            "frequency",
            "duration_days",
            "instruction",
            "created_at",
            "updated_at",
        )

        def has_add_permission(self, request, obj=None):
            return False

    inlines = (PrescriptionItemInline,)
    list_display = ("id", "medical_record", "clinic", "staff", "created_at")
    search_fields = (
        "medical_record__id",
        "clinic__name",
        "staff__username",
        "staff__full_name",
    )
    list_filter = ("clinic", "staff", "created_at")
    readonly_fields = (
        "medical_record",
        "clinic",
        "staff",
        "note",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "appointment",
        "owner",
        "clinic",
        "formatted_amount",
        "method",
        "status",
        "paid_at",
        "created_at",
    )
    search_fields = (
        "appointment__id",
        "owner__username",
        "owner__full_name",
        "clinic__name",
        "transaction_code",
    )
    list_filter = ("status", "method", "clinic", "paid_at", "created_at")
    readonly_fields = (
        "appointment",
        "owner",
        "clinic",
        "amount",
        "method",
        "status",
        "paid_at",
        "transaction_code",
        "note",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Số tiền")
    def formatted_amount(self, obj):
        return f"{obj.amount:,.0f} VND".replace(",", ".")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
