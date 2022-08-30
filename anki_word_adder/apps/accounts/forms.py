from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from .models import Learner


class LearnerCreationForm(UserCreationForm):
    """Form for creating a new user"""

    class Meta(UserCreationForm.Meta):
        model = Learner

    def __init__(self, *args, **kwargs):
        super(LearnerCreationForm, self).__init__(*args, **kwargs)
        # Add attributes for bootstrap
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.name


class LearnerAuthenticationForm(AuthenticationForm):
    """Form for logging a user in"""

    def __init__(self, *args, **kwargs):
        super(LearnerAuthenticationForm, self).__init__(*args, **kwargs)
        # Add attributes for bootstrap
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.name
