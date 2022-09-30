from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import *
from .forms import *
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import DeleteView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime

# Login Page
def user_login(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('../')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'socialmedia/login.html')

# Log user out
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('../')

# Register Page
def register(request):

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'socialmedia/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})

# The Friend List part
class FriendList(ListView):
    model = AppUser
    context_object_name = 'friend_list'
    template_name = 'socialmedia/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = AppUser.objects.get(user=self.request.user)

        try:
            friends = [{'id': friend.user1.id if friend.user1 != user else friend.user2.id,
                        'name': friend.user1.user if friend.user1 != user else friend.user2.user,
                        'images': Image.objects.filter(user=friend.user1 if friend.user1 != user else friend.user2),
                        'date': friend.date,
                        'chat': friend.chat,
                        'friendshipPK': friend.pk}
                       for friend in user.getFriends()]
        except:
            friends = "No friends available"

        context['friend_list'] = friends
        return context

# User profile part
class UserDetail(DetailView):
    model = AppUser
    template_name = 'socialmedia/user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = AppUser.objects.get(user=self.request.user)

        userDetail = AppUser.objects.get(pk=self.kwargs['pk'])
        try:
            images = Image.objects.filter(user=userDetail)
        except Image.DoesNotExist:
            images = "No images available"

        try:
            statuses = Status.objects.filter(user=userDetail)
        except Status.DoesNotExist:
            statuses = "No statuses available"

        # Getting the Friend List
        friendList = FriendList(**kwargs)
        friendList.object_list = ""
        friendList.request = self.request
        friends = friendList.get_context_data(**kwargs).get('friend_list')

        context['friend_list'] = friends
        context['userDetail'] = {'user': userDetail,
                                 'images': images, 'statuses': statuses}
        context['currentUser'] = user
        context['user'] = self.request.user
        return context

# Remove a friend from the Friend List
class FriendDelete(DeleteView):
    model = UserUserFriend
    success_url = "/"

    def post(self, request, *args, **kwargs):
        currentUser = AppUser.objects.get(user=self.request.user)
        friend = AppUser.objects.get(pk=self.kwargs['pk'])
        unfriend = UserUserFriend.objects.filter((Q(user1=currentUser) & Q(
            user2=friend)) | (Q(user1=friend) & Q(user2=currentUser)))
        unfriend.delete()
        return HttpResponseRedirect('/')

# Add a user to the Friend List
def friendCreate(request, pk):
    currentUser = AppUser.objects.get(user=request.user)
    friend = AppUser.objects.get(pk=pk)
    if not UserUserFriend.objects.filter((Q(user1=currentUser) & Q(user2=friend)) | (Q(user1=friend) & Q(user2=currentUser))):
        newfriend = UserUserFriend(user1=currentUser, user2=friend)
        newfriend.save()
    return HttpResponseRedirect('/')

# Update the chat between two fiends
def chatUpdate(request, pk):
    chatObject = UserUserFriend.objects.get(pk=pk)
    chatObject.chat += request.POST.get('chat')
    chatObject.save(update_fields=['chat'])
    return HttpResponseRedirect('/')

# Remove a post from the current user posts
class StatusDelete(DeleteView):
    model = Status
    success_url = "/"

    def get(self, request, *args, **kwargs):
        status = Status.objects.get(pk=self.kwargs['pk'])
        status.delete()
        return HttpResponseRedirect('/')

# add a post to the current user posts
def statusCreate(request):
    currentUser = AppUser.objects.get(user=request.user)
    newStatus = Status(user=currentUser, status=request.POST.get('status'))
    newStatus.save()
    return HttpResponseRedirect('/')

# Edit the post with the passed pk
def statusUpdate(request, pk):
    currentUser = AppUser.objects.get(user=request.user)
    status = Status(pk=pk)
    status.status = request.POST.get('status')
    status.lastDate = datetime.now()
    status.save(update_fields=['status', 'lastDate'])
    return HttpResponseRedirect('/')

# add an image to the current user images
def imagesCreate(request):
    currentUser = AppUser.objects.get(user=request.user)

    for file in request.FILES.getlist('images'):
        newImage = Image(user=currentUser, image=file, name=file.name)
        newImage.save()

    return HttpResponseRedirect('/')

# delete an image from the current user images
class ImageDelete(DeleteView):
    model = Image
    success_url = "/"

    def get(self, request, *args, **kwargs):
        image = Image.objects.get(pk=self.kwargs['pk'])
        image.delete()
        return HttpResponseRedirect('/')

# The search results part
class Search(ListView):
    model = AppUser
    context_object_name = 'friend_list'
    template_name = 'socialmedia/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all users except the current user
        nonFriends = AppUser.objects.filter(~Q(user=self.request.user))
        nonFriendsList = []

        # Remove all current friends from the list
        friendList = FriendList(**kwargs)
        friendList.object_list = ""
        friendList.request = self.request
        friends = friendList.get_context_data(**kwargs).get('friend_list')
        for nonfriend in nonFriends:
            if nonfriend.user not in [f['name'] for f in friends]:
                nonFriendsList.append(
                    {'user': nonfriend, 'image': Image.objects.filter(user=nonfriend)})

        context['friend_list'] = friends
        context['nonfriends_list'] = nonFriendsList
        context['currentUser'] = AppUser.objects.get(user=self.request.user)
        context['user'] = self.request.user
        return context

# Home page redirects to the current user page
def home(request):
    try:
        user = AppUser.objects.get(user=request.user)
    except AppUser.DoesNotExist:
        user = "No User available"

    return HttpResponseRedirect('/user/' + str(user.pk))
