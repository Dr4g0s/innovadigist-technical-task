from django.db import models



class Contact(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class ContactNumber(models.Model):
    contact = models.ForeignKey(Contact, related_name="numbers", on_delete=models.CASCADE)
    number = models.CharField(max_length=100)

    def __str__(self):
        return self.number
