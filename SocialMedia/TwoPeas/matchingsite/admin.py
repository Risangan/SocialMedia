from django.contrib import admin
from .models import *
#from .models import Profile, Hobby #Allows you to see these tables in the Admin Interface

class ProfileAdmin(admin.ModelAdmin):
    fields = ('username','password','gender','email','profileImage','dateOfBirth','hobbies','likes')
    list_display = ('username','password')
    ordering = ['username']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Hobby)