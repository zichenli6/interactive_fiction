from django.db import models

# Create your models here.

class Profile(models.Model):
    name = models.CharField("Name", default="", max_length=64)
    persona = models.TextField("Persona", default="")
    appearance = models.TextField("Appearance", default="")
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name
