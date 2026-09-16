from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

from src.common.base_model import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Tên đăng nhập là bắt buộc.")
        if not email:
            raise ValueError("Email là bắt buộc.")

        email = self.normalize_email(email)
        extra_fields.setdefault("role", User.ROLE_PET_OWNER)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields["role"] = User.ROLE_ADMIN
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True
        extra_fields["clinic"] = None

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser phải có is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser phải có is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    ROLE_PET_OWNER = "PET_OWNER"
    ROLE_CLINIC_STAFF = "CLINIC_STAFF"
    ROLE_ADMIN = "ADMIN"

    ROLE_CHOICES = [
        (ROLE_PET_OWNER, "Chủ thú cưng"),
        (ROLE_CLINIC_STAFF, "Nhân viên phòng khám"),
        (ROLE_ADMIN, "Quản trị viên"),
    ]

    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_PET_OWNER,
        verbose_name="Vai trò",
    )

    clinic = models.ForeignKey(
        "src.Clinic",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_users",
        verbose_name="Phòng khám",
    )

    REQUIRED_FIELDS = ["email", "full_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def clean(self):
        super().clean()

        if self.role == self.ROLE_CLINIC_STAFF and not self.clinic:
            raise ValidationError(
                {"clinic": "Nhân viên phòng khám bắt buộc phải thuộc một phòng khám."}
            )

        if self.role in [self.ROLE_PET_OWNER, self.ROLE_ADMIN] and self.clinic is not None:
            raise ValidationError(
                {"clinic": "Chỉ nhân viên phòng khám mới được phép thuộc một phòng khám."}
            )

        if self.role == self.ROLE_ADMIN:
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.role}"


class StaffUser(User):
    class Meta:
        proxy = True
        verbose_name = "Nhân viên phòng khám"
        verbose_name_plural = "Nhân viên phòng khám"
