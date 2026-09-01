from django.contrib.auth.mixins import UserPassesTestMixin


class ProfileOwnerOrStaffMixin(UserPassesTestMixin):
    raise_exception = True
    def test_func(self):
        """Проверка прав"""
        profile = self.get_object()
        user = self.request.user
        return user.is_staff or user == profile.user