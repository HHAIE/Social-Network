from django.urls import path
from . import views
from . import api
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # parts of the main page
    path('', login_required(login_url='login')(views.home), name='index'),
    path('user/<int:pk>', login_required(login_url='register')
         (views.UserDetail.as_view()), name='user'),
    path('search/', login_required(login_url='login')
         (views.Search.as_view()), name='search'),

    # Friends routes
    path('remove/user/<int:pk>', login_required(login_url='login')
         (views.FriendDelete.as_view()), name='remove_friend'),
    path('add/user/<int:pk>', login_required(login_url='login')
         (views.friendCreate), name='add_friend'),
    path('update/chat/<int:pk>', login_required(login_url='login')
         (views.chatUpdate), name='update_chat'),

    # Posts routes
    path('add/post/', login_required(login_url='login')
         (views.statusCreate), name='add_status'),
    path('remove/post/<int:pk>', login_required(login_url='login')
         (views.StatusDelete.as_view()), name='remove_status'),
    path('update/post/<int:pk>', login_required(login_url='login')
         (views.statusUpdate), name='update_status'),
    
    # Images routes
    path('add/image/', login_required(login_url='login')
         (views.imagesCreate), name='add_images'),
    path('remove/image/<int:pk>', login_required(login_url='login')
         (views.ImageDelete.as_view()), name='remove_image'),

    # User authentication routes
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', login_required(login_url='login')
         (views.user_logout), name='logout'),

    # Api routes
    path('api/user/<int:pk>', api.UserDetail.as_view(), name="user_api"),
    path('api/users/', api.UserList.as_view(), name="users_api"),
    path('api/status/<int:pk>', api.StatusDetail.as_view(), name="status_api"),
    path('api/statuses/', api.StatusList.as_view(), name="statuses_api"),
    path('api/images/', api.ImageList.as_view(), name="images_api"),
    path('api/image/<int:pk>', api.ImageDetail.as_view(), name="image_api"),
]
