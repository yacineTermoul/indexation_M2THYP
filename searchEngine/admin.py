from django.contrib import admin
from .models import Document
from .models import Dictionary
from .models import Website

# Register your models here.
admin.site.register(Document)

admin.site.register(Dictionary)

admin.site.register(Website)