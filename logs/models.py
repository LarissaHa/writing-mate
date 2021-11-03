from django.conf import settings
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import timezone
from django.db.models import Sum


class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    profile_image = models.ImageField(upload_to='images', default=None, null=True, blank=True)
    header_image = models.ImageField(upload_to='images', default=None, null=True, blank=True)
    color = models.CharField(max_length=7, default="#5a5c69", null=True, blank=True)
    is_public = models.BooleanField(default=False)
    about_me = models.TextField(default="", null=True, blank=True)

    pinterest = models.URLField(default="", null=True, blank=True)
    spotify = models.URLField(default="", null=True, blank=True)
    instagram = models.URLField(default="", null=True, blank=True)
    twitter = models.URLField(default="", null=True, blank=True)
    goodreads = models.URLField(default="", null=True, blank=True)
    nanowrimo = models.URLField(default="", null=True, blank=True)

    daily_goal = models.IntegerField(null=True, blank=True)
    UNITS = [
        ("words", 'words'),
        ("characters", 'characters'),
        ("pages", 'pages'),
        ("minutes", 'minutes'),
        ("hours", 'hours'),
        ("other", 'other'),
    ]
    goal_unit = models.CharField(
        max_length=20,
        choices=UNITS,
        default="words",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    date = models.DateField(default="")
    time = models.TimeField(default="")
    count = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    is_update = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return str("{0} ({1} {2})".format(self.project, self.date, self.time))


class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="")
    subtitle = models.CharField(max_length=300, default="", null=True, blank=True)
    slug = models.SlugField(default="")
    created_at = models.DateTimeField(default="")
    goal = models.IntegerField(default=50000)
    deadline = models.DateField(default="", null=True, blank=True)
    topic = models.CharField(max_length=200, default="", null=True, blank=True)
    synopsis = models.TextField(default="", null=True, blank=True)
    excerpt = models.TextField(default="", null=True, blank=True)
    pinterest = models.URLField(default="", null=True, blank=True)
    spotify = models.URLField(default="", null=True, blank=True)
    image = models.ImageField(upload_to='images', default=None, null=True, blank=True)
    color = models.CharField(max_length=7, default="#6f42c1", null=True, blank=True)
    is_public = models.BooleanField(default=False)
    PRIORITY = [
        (1, '1 - high priority'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5 - default'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9 - low priority'),
    ]
    priority = models.IntegerField(choices=PRIORITY, default=5)
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
