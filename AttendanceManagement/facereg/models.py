from django.db import models

class AttendanceImage(models.Model):
    image = models.ImageField(upload_to='attendance_images/')
    timestamp = models.DateTimeField(auto_now_add=True)
 