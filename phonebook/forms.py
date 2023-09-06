from django import forms
from django.forms import inlineformset_factory

from phonebook.models import Contact, ContactNumber

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ('name',)

class ContactNumberForm(forms.ModelForm):

    class Meta:
        model = ContactNumber
        fields = ('contact', 'number')


ContactNumberFormSet = inlineformset_factory(
    Contact,
    ContactNumber,
    form=ContactNumberForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)
