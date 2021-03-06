from django.conf import settings
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import timezone
from django.db.models import Sum


class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #picture = models.ImageField(upload)


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    count = models.IntegerField()
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return str("{0} ({1} {2})".format(self.project, self.date, self.time))


class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="")
    slug = models.SlugField(default="")
    created_at = models.DateTimeField(default=timezone.now)
    goal = models.IntegerField(default=50000)
    STATUS = [
        ("prepping", 'prepping'),
        ("in progress", 'in progress'),
        ("drafted", 'drafted'),
        ("completed", 'completed'),
        ("published", 'published'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="prepping",
    )
    # picture = models.ImageField()
    topic = models.CharField(max_length=200, default="")
    UNITS = [
        ("words", 'words'),
        ("characters", 'characters'),
        ("pages", 'pages'),
        ("minutes", 'minutes'),
        ("hours", 'hours'),
        ("other", 'other'),
    ]
    unit = models.CharField(
        max_length=20,
        choices=UNITS,
        default="words",
    )
    TYPES = [
        ("novel", 'novel'),
        ("short story", 'short story'),
        ("memoir", 'memoir'),
        ("script", 'script'),
        ("nonfiction", 'nonfiction'),
        ("poetry", 'poetry'),
        ("other", 'other'),
    ]
    type = models.CharField(
        max_length=20,
        choices=TYPES,
        default="novel",
    )

    def __str__(self):
        return self.title
