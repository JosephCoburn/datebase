from django.contrib import admin
from .models import Match, Rdv, Match_photo, User_photo, Profile, Match_notes
# Register your models here.
admin.site.register(Match)
admin.site.register(Rdv)
admin.site.register(Match_photo)
admin.site.register(User_photo)
admin.site.register(Profile)
admin.site.register(Match_notes)