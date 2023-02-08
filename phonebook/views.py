from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from phonebook.models import Contact, ContactNumber
from phonebook.forms import ContactForm, ContactNumberFormSet


class ContactInline():
    form_class = ContactForm
    model = Contact
    template_name = "contacts/contact_create_or_update.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('phonebook:list_contacts')

    def formset_numbers_valid(self, formset):
        """
        Hook for custom formset saving. Useful if you have multiple formsets
        """
        numbers = formset.save(commit=False)  # self.save_formset(formset, contact)

        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        
        for number in numbers:
            number.contact = self.object
            number.save()


class ContactCreate(ContactInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(ContactCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'numbers': ContactNumberFormSet(prefix='numbers'),
            }
        else:
            return {
                'numbers': ContactNumberFormSet(
                    self.request.POST or None, self.request.FILES or None, prefix='numbers'),
            }


class ContactUpdate(ContactInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ContactUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'numbers': ContactNumberFormSet(
                self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='numbers'),
        }


class ContactList(ListView):
    model = Contact
    template_name = "contacts/contact_list.html"
    context_object_name = "contacts"


def delete_number(request, pk):
    try:
        number = ContactNumber.objects.get(id=pk)
    except ContactNumber.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('phonebook:update_contact', pk=number.contact.id)

    number.delete()
    messages.success(
            request, 'Number deleted successfully'
            )
    return redirect('phonebook:update_contact', pk=number.contact.id)
