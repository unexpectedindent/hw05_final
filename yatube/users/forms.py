from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    """
    Creates a base user-form.
    Fields: first_name, last_name, username (login), password.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', )
