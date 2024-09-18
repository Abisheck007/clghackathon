from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField()
    image_name = forms.CharField(max_length=100)
