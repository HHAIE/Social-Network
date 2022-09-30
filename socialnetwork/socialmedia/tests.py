import json
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .model_factories import *
from .serializers import *
from channels.testing import WebsocketCommunicator

from socialnetwork.routing import application
from celery.contrib.testing.worker import start_worker
from socialnetwork.celery import app
from celery.contrib.testing.app import TestApp
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as img
import os

# Testing Celery tasks
class CeleryTaskTest(SimpleTestCase):
    databases = '__all__'
    image1 = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestApp()

        # Creating a physical copy of the fake image so make_thumbnail find a file to work on
        image = img.new(mode="RGB", size=(200, 200))
        image.save("images/test.jpg")
        byteArr = io.BytesIO()
        image.save(byteArr, format='jpeg')
        file = SimpleUploadedFile("test1.jpg", byteArr.getvalue())
        image1 = ImageFactory.create(pk=1, image=file)

        # Starting a celery worker
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        Image.objects.all().delete()
        ImageFactory.reset_sequence(0)

        # Deleting the images created for testing
        dir = 'images/'
        for file in os.listdir(dir):
            fileDir = os.path.join(dir, file)
            if "test" in fileDir:
                os.remove(fileDir)

        cls.celery_worker.__exit__(None, None, None)

    def setUp(self):
        super().setUp()
        self.image1 = Image.objects.get(pk=1)

    def test_thumbnailCreated(self):
        self.assertTrue(self.image1.thumbnail)

    def test_thumbnailHasCorrectName(self):
        # The testing worker may run several times, so the thumbnail name may have added text
        self.assertIn('thumb_'+str(self.image1.image)
                      [:-4], str(self.image1.thumbnail))

# Testing the WebSocket/Channels
class WebSocketTest(TestCase):

    async def test_Consumer(self):
        communicator = WebsocketCommunicator(application, "/ws/chat/1")
        connected, subprotocol = await communicator.connect()
        assert connected

        # Send chat_message to WebSocket
        await communicator.send_json_to({"type": "chat_message", "message": "hi"})

        # Test receiving the chat_message
        message = await communicator.receive_json_from()
        self.assertDictEqual(message, {"message": "hi"})

        # Close
        await communicator.disconnect()

# Testing user serializer function
class UserSerialiserTest(APITestCase):
    user1 = None
    userSerializer = None

    def setUp(self):
        self.user1 = UserFactory.create(username="test1")
        self.userSerializer = UserSerializer(instance=self.user1)

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)

    def test_UserSerilaiserHasCorrectFields(self):
        data = self.userSerializer.data
        self.assertEqual(set(data.keys()), set(['username', 'email', 'id']))

    def test_UserSerilaiserHasCorrectData(self):
        data = self.userSerializer.data
        self.assertEqual(data['username'], "test1")

# Testing AppUser serializer function
class AppUserSerialiserTest(APITestCase):
    user1 = None
    userSerializer = None

    def setUp(self):
        user = UserFactory(username="test1")
        self.user1 = AppUserFactory.create(user=user)
        self.userSerializer = AppUserSerializer(instance=self.user1)

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_AppUserSerilaiserHasCorrectFields(self):
        data = self.userSerializer.data
        self.assertEqual(set(data.keys()), set(
            ['user', 'birthDate', 'images', 'statuses', 'friend_user1', 'friend_user2']))

    def test_AppUserSerilaiserHasCorrectData(self):
        data = self.userSerializer.data
        self.assertEqual(data['user']['username'], "test1")

# Testing image serializer function
class ImageSerialiserTest(APITestCase):
    image1 = None
    imageSerializer = None
    imageListSerializer = None

    def setUp(self):
        self.image1 = ImageFactory.create(name="test1")
        self.imageSerializer = ImageSerializer(instance=self.image1)
        self.imageListSerializer = ImageListSerializer(instance=self.image1)

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        Image.objects.all().delete()
        ImageFactory.reset_sequence(0)

    def test_imageSerilaiserHasCorrectFields(self):
        data = self.imageSerializer.data
        self.assertEqual(set(data.keys()), set(['name', 'image', 'user']))

    def test_imageListSerilaiserHasCorrectFields(self):
        data = self.imageListSerializer.data
        self.assertEqual(set(data.keys()), set(
            ['name', 'image', 'thumbnail', 'user']))

    def test_imageSerilaiserHasCorrectData(self):
        data = self.imageSerializer.data
        self.assertEqual(data['name'], "test1")

    def test_imageListSerilaiserHasCorrectData(self):
        data = self.imageListSerializer.data
        self.assertEqual(data['name'], "test1")

# Testing status serializer function
class StatusSerialiserTest(APITestCase):
    status1 = None
    statusSerializer = None

    def setUp(self):
        self.status1 = StatusFactory.create(status='Good Day')
        self.statusSerializer = StatusSerializer(instance=self.status1)

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        Status.objects.all().delete()
        StatusFactory.reset_sequence(0)

    def test_statusSerilaiserHasCorrectFields(self):
        data = self.statusSerializer.data
        self.assertEqual(set(data.keys()), set(
            ['status', 'date', 'lastDate', 'user']))

    def test_statusSerilaiserHasCorrectData(self):
        data = self.statusSerializer.data
        self.assertEqual(data['status'], 'Good Day')

# Testing UserUserFriend serializer function
class UserUserFriendSerialiserTest(APITestCase):
    userUserFriend1 = None
    userUserFriendSerializer = None

    def setUp(self):
        self.userUserFriend1 = UserUserFriendFactory.create(chat='Hi')
        self.userUserFriendSerializer = UserUserFriendSerializer(
            instance=self.userUserFriend1)

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserUserFriend.objects.all().delete()
        UserUserFriendFactory.reset_sequence(0)

    def test_userUserFriendSerilaiserHasCorrectFields(self):
        data = self.userUserFriendSerializer.data
        self.assertEqual(set(data.keys()), set(
            ['user1', 'user2', 'date', 'chat']))

    def test_userUserFriendSerilaiserHasCorrectData(self):
        data = self.userUserFriendSerializer.data
        self.assertEqual(data['chat'], 'Hi')

# Testing user Api
class UserTest(APITestCase):

    user1 = None
    user2 = None
    good_url = ''
    users_list_url = ''
    bad_url = ''
    delete_url = ''

    def setUp(self):
        user1 = UserFactory.create(username='test1')
        user2 = UserFactory.create(username='test2')
        user3 = UserFactory.create(username='test3')
        self.user1 = AppUserFactory.create(pk=1, user=user1)
        self.user1 = AppUserFactory.create(pk=2, user=user2)
        self.user3 = AppUserFactory.create(pk=3, user=user3)
        self.delete_url = reverse('user_api', kwargs={'pk': 3})
        self.good_url = reverse('user_api', kwargs={'pk': 1})
        self.bad_url = "/api/user/H/"
        self.users_list_url = "/api/users/"

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_userAPIReturnsSuccess(self):
        response = self.client.get(self.good_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_userAPIReturnsCorrectData(self):
        response = self.client.get(self.good_url, format='json')
        data = json.loads(response.content)
        self.assertTrue('user' in data)

    def test_userAPIReturnFailOnBadPk(self):
        response = self.client.get(self.bad_url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_userAPIDeleteIsSuccessful(self):
        response = self.client.delete(self.delete_url, format='json')
        self.assertEqual(response.status_code, 204)

    def test_usersListAPIReturnsSuccess(self):
        response = self.client.get(self.users_list_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_usersListAPIReturnsCorrectData(self):
        response = self.client.get(self.users_list_url, format='json')
        data = json.loads(response.content)
        self.assertTrue('user' in data[0])

# Testing image Api
class ImageTest(APITestCase):

    image1 = None
    image2 = None
    good_url = ''
    images_list_url = ''
    bad_url = ''
    delete_url = ''

    def setUp(self):
        self.image1 = ImageFactory.create(pk=1, name='test1')
        self.image1 = ImageFactory.create(pk=2, name='test2')
        self.image3 = ImageFactory.create(pk=3, name='test3')
        self.delete_url = reverse('image_api', kwargs={'pk': 3})
        self.good_url = reverse('image_api', kwargs={'pk': 1})
        self.bad_url = "/api/image/H/"
        self.images_list_url = "/api/images/"

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        Image.objects.all().delete()
        ImageFactory.reset_sequence(0)

    def test_imageAPIReturnsSuccess(self):
        response = self.client.get(self.good_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_imageAPIReturnsCorrectData(self):
        response = self.client.get(self.good_url, format='json')
        data = json.loads(response.content)
        self.assertTrue('image' in data)

    def test_imageAPIReturnFailOnBadPk(self):
        response = self.client.get(self.bad_url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_imageAPIDeleteIsSuccessful(self):
        response = self.client.delete(self.delete_url, format='json')
        self.assertEqual(response.status_code, 204)

    def test_imagesListAPIReturnsSuccess(self):
        response = self.client.get(self.images_list_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_imagesListAPIReturnsCorrectData(self):
        response = self.client.get(self.images_list_url, format='json')
        data = json.loads(response.content)
        self.assertTrue('image' in data[0])

# Testing status Api
class StatusTest(APITestCase):

    status1 = None
    status2 = None
    good_url = ''
    statuses_list_url = ''
    bad_url = ''
    delete_url = ''

    def setUp(self):
        self.status1 = StatusFactory.create(pk=1, status='test1')
        self.status1 = StatusFactory.create(pk=2, status='test2')
        self.status3 = StatusFactory.create(pk=3, status='test3')
        self.delete_url = reverse('status_api', kwargs={'pk': 3})
        self.good_url = reverse('status_api', kwargs={'pk': 1})
        self.bad_url = "/api/status/H/"
        self.statuses_list_url = "/api/statuses/"

    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence(0)
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        Status.objects.all().delete()
        StatusFactory.reset_sequence(0)

    def test_statusAPIReturnsSuccess(self):
        response = self.client.get(self.good_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_statusAPIReturnsCorrectData(self):
        response = self.client.get(self.good_url, format='json')
        data = json.loads(response.content)
        self.assertTrue('status' in data)

    def test_statusAPIReturnFailOnBadPk(self):
        response = self.client.get(self.bad_url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_statusAPIDeleteIsSuccessful(self):
        response = self.client.delete(self.delete_url, format='json')
        self.assertEqual(response.status_code, 204)

    def test_statusesListAPIReturnsSuccess(self):
        response = self.client.get(self.statuses_list_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_statusesListAPIReturnsCorrectData(self):
        response = self.client.get(self.statuses_list_url, format='json')
        data = json.loads(response.content)
        self.assertTrue('status' in data[0])
