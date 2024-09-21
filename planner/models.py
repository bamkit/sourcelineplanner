from django.db import models
from django.utils import timezone

class File(models.Model):
    name = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Point(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='points')
    shotpoint = models.IntegerField()
    east = models.FloatField()
    north = models.FloatField()

    def __str__(self):
        return f"{self.file.name} - Shotpoint {self.shotpoint}: ({self.east}, {self.north})"

class Polygon(models.Model):
    name = models.CharField(max_length=100)
    coordinates = models.TextField()  # Store as JSON string

    def __str__(self):
        return self.name
    
class PreplotLine(models.Model):
    linename = models.IntegerField()
    shotpoint1 = models.IntegerField(default=0)
    eastings1 = models.FloatField()
    northings1 = models.FloatField()
    latitude1 = models.FloatField()
    longitude1 = models.FloatField()
    shotpoint2 = models.IntegerField(default=0)
    eastings2 = models.FloatField()
    northings2 = models.FloatField()
    latitude2 = models.FloatField()
    longitude2 = models.FloatField()

    def __str__(self):
        return f"Line {self.linename}: {self.shotpoint1} - {self.shotpoint2}"

class SequenceFile(models.Model):
    preplot_number = models.IntegerField()
    type = models.IntegerField()
    pass_number = models.IntegerField()
    sequence_number = models.IntegerField()
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    linename = models.CharField(null=True, max_length=255)
    
    def __str__(self):
        return f"Sequence {self.linename} - {self.preplot_number}-{self.type}-{self.pass_number}-{self.sequence_number}"

class SequenceFileDetail(models.Model):
    sequence_file = models.ForeignKey(SequenceFile, null=True, on_delete=models.CASCADE, related_name='details')
    sp = models.IntegerField()
    lat = models.FloatField()
    long = models.FloatField()
    east = models.FloatField()
    north = models.FloatField()
    depth = models.FloatField()
    datetime = models.DateTimeField()
    zlat1 = models.FloatField()
    zlon1 = models.FloatField()
    zlat2 = models.FloatField()
    zlon2 = models.FloatField()
    zlat3 = models.FloatField()
    zlon3 = models.FloatField()
    mean_lat = models.FloatField()
    mean_lon = models.FloatField()

    def __str__(self):
        return f"Sequence {self.sequence_file.linename} - SP {self.sp}"
