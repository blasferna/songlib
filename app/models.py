from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Song(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    lyrics = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title


class SetList(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return self.title


class SetListSong(models.Model):
    setlist = models.ForeignKey(SetList, related_name='songs', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    chord = models.CharField(max_length=20)
    

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order} - {self.song}"
