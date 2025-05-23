import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class AlphanumericPasswordValidator:
    regex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d).+$')

    def validate(self, password, user=None):
        if not self.regex.match(password):
            raise ValidationError(
                _("パスワードは英字と数字を組み合わせてください。"),
                code='password_no_alnum',
            )

    def get_help_text(self):
        return _("パスワードは英字と数字を組み合わせてください。")
