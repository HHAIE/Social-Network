from unicodedata import category
import factory
from random import randint
from random import choice

from django.test import TestCase
from django.conf import settings
from django.core.files import File

from .models import *

# Create random user
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('name')
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)

    class Meta:
        model = User

# Create random AppUser
class AppUserFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    birthDate = factory.Faker('date')

    class Meta:
        model = AppUser

# Create random image
class ImageFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    image = factory.Faker('file_name', category='image')
    user = factory.SubFactory(AppUserFactory)

    class Meta:
        model = Image

# Create random post
class StatusFactory(factory.django.DjangoModelFactory):
    status = factory.Faker('sentence')
    date = factory.Faker('date')
    lastDate = factory.Faker('date')
    user = factory.SubFactory(AppUserFactory)

    class Meta:
        model = Status

# Create random friend
class UserUserFriendFactory(factory.django.DjangoModelFactory):
    user1 = factory.SubFactory(AppUserFactory)
    user2 = factory.SubFactory(AppUserFactory)
    date = factory.Faker('date')

    class Meta:
        model = UserUserFriend
