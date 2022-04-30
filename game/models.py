from django.db import models
import os

# Create your models here.

def update_filename(instance, filename):
    return os.path.join("images", "profile.png")


class Profile(models.Model):
    name = models.CharField("Name", default="", max_length=64)
    persona = models.TextField("Persona", default="")
    appearance = models.TextField("Appearance", default="")
    image = models.ImageField(upload_to=update_filename, blank=True, null=True)

    def __str__(self):
        return self.name
