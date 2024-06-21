from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password

User = ""  # here get your user object form your model


class SettingsBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        login_valid = (settings.ADMIN_LOGIN == username)
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            return User.objects.get(id=username)
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
