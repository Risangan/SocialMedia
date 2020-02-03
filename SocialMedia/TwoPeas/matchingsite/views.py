from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Profile, Hobby
from .serializers import ProfileSerializer
from .serializers import HobbySerializer
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.template import RequestContext, loader
from django.utils import timezone
from django.http import HttpResponse, Http404
from datetime import date
from django.utils.timezone import now
from django.db.models import Q
from django.core.mail import send_mail

#Datetime library to get time for setting cookie
import datetime as D
import sys

appname = 'TwoPeas'

#Main Page
def index(request):
    context = { 'appname': appname }
    return render(request,'matchingsite/index.html',context)

#Returns a JSON response of the API view for the model: Profile (All registered users)
def getUsers(request):
    users = Profile.objects.all()
    serializer = ProfileSerializer(users, many=True) 
    return JsonResponse(serializer.data, safe=False)

#Returns a JSON response of the API view for the model: Hobby (All hobbies are predefined)
def getHobbies(request):
    hobbies = Hobby.objects.all()
    serializer = HobbySerializer(hobbies, many=True) 
    return JsonResponse(serializer.data, safe=False)

#Decorator that tests whether user is logged in. Adds 'user' parameter, so we can retrieve info about the logged-in user
def loggedin(view):
    def mod_view(request):
        if 'username' in request.session:
            username = request.session['username']
            try: user = Profile.objects.get(username=username)
            except Profile.DoesNotExist: raise Http404('Member does not exist')
            return view(request, user)
        else:
            return render(request,'matchingsite/not-logged-in.html',{})
    return mod_view

#View for the Login Page. Create session for logged-in user here. Adapted from 'socialnetwork' app. 
def login(request):
    if not ('username' in request.POST and 'password' in request.POST):
        context = { 'appname': appname }
        return render(request,'matchingsite/login.html',context)
    else:
        username = request.POST['username']
        password = request.POST['password']
        try: member = Profile.objects.get(username=username)
        except Profile.DoesNotExist: raise Http404('User does not exist')
        #Check if it is the correct password user input here.       
        if member.check_password(password):           
            # remember user in session variable
            request.session['username'] = username
            request.session['password'] = password
            context = {
               'appname': appname,
               'username': username,
               'loggedin': True
            }
            response = render(request, 'matchingsite/login.html', context)
            # remember last login in cookie
            now = D.datetime.utcnow()
            max_age = 365 * 24 * 60 * 60  #one year
            delta = now + D.timedelta(seconds=max_age)
            format = "%a, %d-%b-%Y %H:%M:%S GMT"
            expires = D.datetime.strftime(delta, format)
            response.set_cookie('last_login',now,expires=expires)
            return response
        else:
            raise Http404(member)

#View for SignUp Page
def signup(request):
    context = { 'appname': appname }
    return render(request,'matchingsite/signup.html',context)

#This view runs when the user has input all their details in the SignUp page and submitted the form.
def register(request):
    #The HTML checks if all the forms are filled in anyway before it can be submitted. Nevertheless, this also checks if the username/password field have values.    
    if 'username' in request.POST and 'password' in request.POST:
        #As a POST request, plug all the values POSTED from the JQuery into variables
        u = request.POST['username']
        p = request.POST['password']
        dob = request.POST['dob']
        e = request.POST['emailaddress']
        g = request.POST['gender']
        pp = "/media/profile_images/defaultpic.jpg"
        #Create new Profile Object with all that information. Profile Image/Hobbies can be changed later when logged on.
        Profile.objects.create(
            username = u,
            dateOfBirth = dob,
            password = make_password(p),
            email = e,
            gender = g,
            profileImage = pp
        )
        context = {
            'appname' : appname,
            'username' : u
        }
        #Change the page to confirm the user has registered successfully and pass the new username to it
        return render(request,'matchingsite/user-registered.html',context)
    else:
        raise Http404('POST data missing')

#Any view with the @loggedin decorator can only be used when a user has logged on.
#These views have access to the logged-in user's details
#This view runs when the user logs out
@loggedin
def logout(request, user):
    #This gets rid of the current session as the user is logging out
    request.session.flush()
    context = { 'appname': appname }
    return render(request,'matchingsite/logout.html', context)

#The profile page view. Send relevant information about the logged-in user to it, so we can display the information in the template.
@loggedin
def profile(request, user): 
    #The 'likelist' retrieves all the users that the loggedin user 'likes'. You can 'like' a user in the 'Members' page.
    likeList = []
    profiles = Profile.objects.filter(username=user.username)
    for p in profiles:
        likeList = [sw for sw in p.likes.all()]
    return render(request, 'matchingsite/profile.html', {
        'appname': appname,
        'username': user.username,
        'email': user.email,
        'gender': user.gender,
        'dateOfBirth': user.dateOfBirth,
        'image': user.profileImage.url,
        'age': calculate_age(user.dateOfBirth),
        'likelist': likeList,
        'loggedin': True}
        )

#The Search Page View
@loggedin
def search(request, user): 
    return render(request, 'matchingsite/search.html', {
        'appname': appname,
        'username': user.username,
        'loggedin': True}
        )

#The Members Page View
@loggedin
def members(request, user): 
    #Functionality for when the user 'likes' another user.     
    try:
        # like new member
        if 'add' in request.GET:
            newLikedUser = request.GET['add']
            friend = Profile.objects.get(username=newLikedUser)
            #Save new user to database
            user.likes.add(friend)
            user.save()
            #An email is sent to that user when they are 'liked'
            send_mail(
                'You got a like on TwoPeas!',
                user.username + ' liked you on TwoPeas!',
                'twopeasmatching@gmail.com',
                [friend.email],
                fail_silently=False,
            )
    except Profile.DoesNotExist:
        raise Http404('User does not exist')    
    userHobbiesList = []   
    profiles = Profile.objects.filter(username=user.username)
    for p in profiles:
        userHobbiesList = [sw for sw in p.hobbies.all()]
        print(userHobbiesList)
    #List of all user hobbies for logged-in user
    userHobbies = user.hobbies.all() 
    #List of members that the logged-in user 'likes'
    likes = user.likes.all()
    #All users except logged-in user
    allProfiles = Profile.objects.exclude(username=user.username)
    return render(request, 'matchingsite/members.html', {
        'appname': appname,
        'username': user.username,
        'userHobbies': userHobbies,
        'userHobbiesList' : userHobbiesList,
        'likes' : likes,
        'allProfiles' : allProfiles,
        'loggedin': True}
        )

#Gets list of hobbies for the username that is sent in. This is used in the Members page to find similar members to you. 
@loggedin
def getHobbiesForUser(request, user):
    if request.method == 'GET':
        usernameData = request.GET['username']    
        hobbyList = []
        profiles = Profile.objects.filter(username=usernameData)
        for p in profiles:
                hobbyList = [sw for sw in p.hobbies.all()]
                print(hobbyList)
        serializer = HobbySerializer(hobbyList, many=True) #Convert Model Data to JSON. Serialize all Products.
        return JsonResponse(serializer.data, safe=False) 

#The Set Profile Picture Page view.  
@loggedin
def setProfilePic(request, user): 
    return render(request, 'matchingsite/profile_form.html', {
        'appname': appname,
        'username': user.username,
        'image': user.profileImage.url,
        'loggedin': True}
        )

#The Set Hobbies Page view.
@loggedin
def setHobbies(request, user): 
    hobbies = Hobby.objects.all()
    return render(request, 'matchingsite/hobbies.html', {
        'appname': appname,
        'username': user.username,
        'hobbies' : hobbies,
        'loggedin': True}
        )

#The Upload images view is used in the set Profile Picture page. (adapted from the 'socialnetwork' app)
@loggedin
def upload_image(request, user):
    if 'img_file' in request.FILES:
        image_file = request.FILES['img_file']
        user.profileImage = image_file
        user.save()
        return HttpResponse(user.profileImage.url)
    else:
        raise Http404('Image file not received')

#POST Request for Hobbies Page. When the user saves their new choices of hobbies. 
@loggedin
def postHobby(request, user):
    if request.method == 'POST':
        hobbydata = request.POST.getlist('hobbies[]')
        userHobbies = user.hobbies.all() # List of all previous user hobbies
        #Remove all existing hobbies
        for x in userHobbies:
            user.hobbies.remove(x)
        #Add new hobbies from checklist
        for x in hobbydata:
            newHobby = Hobby.objects.get(hobbyName=x)
            user.hobbies.add(newHobby)
        user.save() 
        #Get new hobbies
        username = user.username
        users = Profile.objects.filter(username=username)
        serializer = ProfileSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

#We use djangorestframework here. This view GETS all the hobbies associated with the logged-in user.
@loggedin
@api_view(['GET', 'PUT', 'DELETE'])
def getUserHobbies(request, user):
    if request.method == 'GET':
        username = user.username
        users = Profile.objects.filter(username=username)
        serializer = ProfileSerializer(users, many=True)
        return Response(serializer.data)

#This view is used in the Members page. A single hobbyName is sent into this view and it returns all the users that like that hobby, excluding the logged-in user.
@loggedin
def getSimilarUsers(request, user):
    if request.method == 'POST':
        hobbydata = request.POST['hobbies']
        #Retrieve Hobby object according to the posted hobbyName
        hobbyFilter = Hobby.objects.filter(hobbyName=hobbydata)
        #Get ID of that hobby object
        hobbyid = hobbyFilter[0].id
        #Returns all the profiles that have selected the hobby with hobbyid (where hobbyid is the id of a hobby that the loggedin user has selected)
        filterProfiles = Profile.objects.filter(hobbies=hobbyid).exclude(username=user.username)
        serializer = ProfileSerializer(filterProfiles, many=True)
        return JsonResponse(serializer.data, safe=False)

#This view simply returns an API view for all registered users, excluding the logged in user.
@loggedin
def getUsersWithoutLogged(request, user):
    users = Profile.objects.exclude(username=user.username)
    serializer = ProfileSerializer(users, many=True)
    return JsonResponse(serializer.data, safe=False)

#This view is used in the Search page to filter profiles based on the inputted search information
@loggedin
def filterSearch(request, user):
    if request.method == 'POST':
        gender = request.POST['gender']
        minAge = request.POST['minAge']
        maxAge = request.POST['maxAge']
        #Converts age to dates
        minDate = convertAge(minAge)
        maxDate = convertAge(maxAge)
        #Returns profiles based on search data
        if gender == "any":
                filterProfiles = Profile.objects.filter(dateOfBirth__gte=maxDate, dateOfBirth__lte=minDate).order_by("dateOfBirth")
        else:
                filterProfiles = Profile.objects.filter(gender=gender).filter(dateOfBirth__gte=maxDate, dateOfBirth__lte=minDate).order_by("dateOfBirth")
        serializer = ProfileSerializer(filterProfiles, many=True)
        return JsonResponse(serializer.data, safe=False)

#Function for calculating age based on date of birth
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

#Function for converting an integer age to a date
def convertAge(age):
    current = date.today()
    this_date = date(current.year - int(age), current.month, current.day)  
    return this_date 