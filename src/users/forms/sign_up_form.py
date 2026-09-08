from allauth.account.forms import SignupForm
from django import forms


class MyCustomSignupForm(SignupForm):
    name = forms.CharField(max_length=50, required=True, label="ПІБ")
    accept_policy = forms.BooleanField(required=True, label="Я згоден з політикою конфіденційності")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Паролі не співпадають.")

        return cleaned_data

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        user.name = self.cleaned_data.get("name")
        user.save()
        return user
