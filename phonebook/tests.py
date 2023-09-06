from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from .models import Contact, ContactNumber
from .forms import ContactNumberFormSet


class ContactListViewTest(TestCase):
    def setUp(self):
        # Create some sample contacts for testing
        self.contact1 = Contact.objects.create(name="John")
        self.contact2 = Contact.objects.create(name="Jane")

    def test_contact_list_view(self):
        # Simulate a GET request to the contact list view
        response = self.client.get(reverse("phonebook:list_contacts"))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the template used for rendering is correct
        self.assertTemplateUsed(response, "contacts/contact_list.html")

        # Check that the contacts are included in the response context
        contacts = response.context["contacts"]
        self.assertQuerysetEqual(
            contacts,
            [repr(self.contact1), repr(self.contact2)],
            ordered=False
        )


class ContactCreateViewTest(TestCase):
    def test_get_context_data(self):
        # Simulate a GET request to the contact create view
        response = self.client.get(reverse("phonebook:create_contact"))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used for rendering
        self.assertTemplateUsed(response, "contacts/contact_create_or_update.html")

        # Check that 'named_formsets' is included in the context
        self.assertTrue("named_formsets" in response.context)

        # Check that the 'named_formsets' context data contains 'numbers' formset
        self.assertIsInstance(response.context["named_formsets"]["numbers"], ContactNumberFormSet)

    def test_get_named_formsets(self):
        # Simulate a GET request to the contact create view
        response = self.client.get(reverse("phonebook:create_contact"))

        # Create a ContactCreate instance
        view = response.context["view"]

        # Check that the 'numbers' formset is created when the request method is GET
        formsets = view.get_named_formsets()
        self.assertIsInstance(formsets["numbers"], ContactNumberFormSet)

        # Simulate a POST request with data
        response = self.client.post(reverse("phonebook:create_contact"), data={"name": "John"})

        # Create a ContactCreate instance
        view = response.context["view"]

        # Check that the 'numbers' formset is created when the request method is POST
        formsets = view.get_named_formsets()
        self.assertIsInstance(formsets["numbers"], ContactNumberFormSet)


class ContactUpdateViewTest(TestCase):
    def setUp(self):
        # Create a sample contact for testing
        self.contact = Contact.objects.create(name="John")

    def test_get_context_data(self):
        # Simulate a GET request to the contact update view
        response = self.client.get(
            reverse("phonebook:update_contact", args=[self.contact.pk])
        )

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used for rendering
        self.assertTemplateUsed(response, "contacts/contact_create_or_update.html")

        # Check that 'named_formsets' is included in the context
        self.assertTrue("named_formsets" in response.context)

        # Check that the 'named_formsets' context data contains 'numbers' formset
        self.assertIsInstance(
            response.context["named_formsets"]["numbers"],
            ContactNumberFormSet
        )

    def test_get_named_formsets(self):
        # Simulate a GET request to the contact update view
        response = self.client.get(
            reverse("phonebook:update_contact", args=[self.contact.pk])
        )

        # Create a ContactUpdate instance
        view = response.context["view"]

        # Check that the 'numbers' formset is created when the request method is GET
        formsets = view.get_named_formsets()
        self.assertIsInstance(formsets["numbers"], ContactNumberFormSet)


class DeleteNumberViewTest(TestCase):
    def setUp(self):
        # Create a sample contact and associated number for testing
        self.contact = Contact.objects.create(name="John")
        self.number = ContactNumber.objects.create(
            contact=self.contact,
            number="1234567890"
        )

    def test_delete_existing_number(self):
        # Simulate a POST request to delete an existing number
        url = reverse("phonebook:delete_number", args=[self.number.pk])
        response = self.client.post(url)

        # Check that the response status code is 302 (Redirect)
        self.assertEqual(response.status_code, 302)

        # Check that the number is deleted from the database
        with self.assertRaises(ContactNumber.DoesNotExist):
            ContactNumber.objects.get(pk=self.number.pk)

        # Check success message in messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Number deleted successfully')

    def test_delete_nonexistent_number(self):
        # Simulate a POST request to delete a non-existing number
        url = reverse("phonebook:delete_number", args=[999])  # Non-existent PK
        response = self.client.post(url)

        # Check that the response status code is 302 (Redirect)
        self.assertEqual(response.status_code, 302)

        # Check error message in messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Object Does not exit')


