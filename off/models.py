from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ManyToManyField(User)
    category = models.ManyToManyField(Category)
    nutriscore = models.CharField(max_length=1)
    name = models.CharField(max_length=1000)
    url_image = models.CharField(max_length=1000, unique=True)
    url_link = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.name
