from src.models import User


class UserRepository:
    @staticmethod
    def create_user(password: str, **kwargs):
        return User.objects.create_user(password=password, **kwargs)

    @staticmethod
    def get_by_id(user_id: int):
        return User.objects.select_related("clinic").filter(id=user_id).first()

    @staticmethod
    def get_by_username(username: str):
        return User.objects.filter(username=username).first()

    @staticmethod
    def get_by_email(email: str):
        return User.objects.filter(email=email).first()

    @staticmethod
    def get_staff_list(clinic_id=None, is_active=None):
        queryset = User.objects.select_related("clinic").filter(role=User.ROLE_CLINIC_STAFF)
        if clinic_id is not None:
            queryset = queryset.filter(clinic_id=clinic_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset.order_by("-created_at")

    @staticmethod
    def save(user: User):
        user.save()
        return user
