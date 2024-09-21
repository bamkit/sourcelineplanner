from django.contrib import admin
from .models import File, Point, Polygon, PreplotLine, SequenceFile, SequenceFileDetail

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('file', 'shotpoint', 'east', 'north')
    list_filter = ('file',)
    search_fields = ('file__name', 'shotpoint')

@admin.register(Polygon)
class PolygonAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

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
