from django.urls import path

from phonebook.views import ContactList, ContactCreate, ContactUpdate, delete_number

app_name = 'phonebook'

urlpatterns = [
    path('', ContactList.as_view(), name='list_contacts'),
    path('create/', ContactCreate.as_view(), name='create_contact'),
    path('update/<int:pk>/', ContactUpdate.as_view(), name='update_contact'),
    path('delete-number/<int:pk>/', delete_number, name='delete_number'),
]
