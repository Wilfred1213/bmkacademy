from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


User = get_user_model()


class UserService:

    @classmethod
    def reset_password(cls, user):

        temporary_password = get_random_string(
            length=10
        )

        user.set_password(
            temporary_password
        )

        user.must_change_password = True

        user.save(
            update_fields=[
                "password",
                "must_change_password",
            ]
        )

        return temporary_password

    @classmethod
    def get_parent_activation_link(cls, user):

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = default_token_generator.make_token(
            user
        )

        return uid, token