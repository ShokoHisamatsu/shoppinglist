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

class CustomMinimumLengthValidator:
    """
    Django 標準の MinimumLengthValidator と同じ機能だが、
    エラーメッセージを日本語にカスタマイズ。
    """
    def __init__(self, min_length=8):
        self.min_length = int(min_length)

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("パスワードが短すぎます。%(min_length)d 文字以上にしてください。") % {"min_length": self.min_length},
                code='password_too_short',
            )

    def get_help_text(self):
        return _("パスワードは %(min_length)d 文字以上で設定してください。") % {"min_length": self.min_length}