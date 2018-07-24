from django import forms


class FindByNameForm(forms.Form):
    name = forms.CharField()
