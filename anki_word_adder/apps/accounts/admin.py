from django.contrib import admin

from .models import Learner, Settings, Word, Translation, Feedback, Request


admin.site.register(Learner)
admin.site.register(Settings)
admin.site.register(Word)
admin.site.register(Translation)
admin.site.register(Feedback)
admin.site.register(Request)
