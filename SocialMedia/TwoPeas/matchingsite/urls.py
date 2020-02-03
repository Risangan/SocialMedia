from django.urls import path
from django.contrib import admin
from . import views
from .models import Profile, Hobby
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # API view for all registered users
    # /users/
    path('users/', views.getUsers, name='users'),

    # API view for all registered users excluding logged-in user. Can only be used when logged-in.
    # /userswithoutlogged/
    path('userswithoutlogged/', views.getUsersWithoutLogged, name='userswithoutlogged'),

    # This view is used in the Members page. A single hobbyName is sent into this view and it returns all the users that like that hobby, excluding the logged-in user.
    # /similarusers/
    path('similarusers/', views.getSimilarUsers, name='similarusers'),

    # API view for all hobbies.
    # /hobbies/
    path('hobbies/', views.getHobbies, name='hobbies'),

    # Main Page
    # /
    path('', views.index, name='index'),

    # Login Page
    # /login/
    path('login/', views.login, name = 'login'),

    # SignUp Page
    # /signup/
    path('signup/', views.signup, name = 'signup'),
    
    # Search Page
    # /search/
    path('search/', views.search, name = 'search'),

    # View runs when a new user registers
    # /register/
	path('register/', views.register, name='register'),

    # View runs when user logs out
    # /logout/
	path('logout/', views.logout, name='logout'),

    # Profile Page
    # /profile/
	path('profile/', views.profile, name='profile'),

    # Search Page
    # /search/
	path('search/', views.search, name='search'),

    # Members Page
    # /members/
	path('members/', views.members, name='members'),

    # Set Hobbies Page
    # /setHobbies/
	path('sethobbies/', views.setHobbies, name='hobbies'),

    # Set Profile Picture Page
    # /update/
    path('update/', views.setProfilePic, name='updatePic'),
	
    # Ajax: upload new profile image
    # /uploadimage/
    path('uploadimage/', views.upload_image, name='uploadimage'),

    # In the Set Hobbies Page, update hobbies
    # /setHobbies/update
    path('sethobbies/update', views.postHobby, name='updateHobby'),

    # Get all hobbies for the LOGGEED-IN user ONLY
    # /getUserHobbies/
    path('getUserHobbies/', views.getUserHobbies, name='getUserHobbies'),

    # Get all hobbies for the SPECIFIED user
    # /loadhobbies/
    path('loadhobbies/', views.getHobbiesForUser, name='loadhobbies'),

    # Filters results in Search page
    # /filtersearch/
    path('filtersearch/', views.filterSearch, name='filtersearch'),
]
