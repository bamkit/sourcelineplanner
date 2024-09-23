from django.contrib import admin
from .models import PreplotLine, SequenceFile, SequenceFileDetail

@admin.register(PreplotLine)
class PreplotLineAdmin(admin.ModelAdmin):
    list_display = ('linename',)
    search_fields = ('linename',)

@admin.register(SequenceFile)
class SequenceFileAdmin(admin.ModelAdmin):
    list_display = ('sequence_number',)
    search_fields = ('sequence_number',)

@admin.register(SequenceFileDetail)
class SequenceFileDetailAdmin(admin.ModelAdmin):
    list_display = ('sp',)
    search_fields = ('sp',)
