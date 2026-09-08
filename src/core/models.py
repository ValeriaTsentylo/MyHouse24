from django.db import models


class Gallery(models.Model):
    pass


class GalleryImage(models.Model):
    alt_text = models.CharField(max_length=20)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.alt_text
