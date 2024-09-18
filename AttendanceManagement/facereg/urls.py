from django.urls import path
from . import views

urlpatterns = [
    path('detect/', views.detect_faces, name='detect_faces'),
    path('upload/', views.upload_image, name='upload_image'),
    path('capture/',views.capture_and_save_image, name='capture_and_save_image'),
    path('',views.index,name="home"),
]
