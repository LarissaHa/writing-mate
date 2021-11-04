from django.conf import settings
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import timezone
from django.db.models import Sum


class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    profile_image = models.ImageField(upload_to='images', verbose_name="Profile Image", help_text="select an image to display yourself", default=None, null=True, blank=True)
    header_image = models.ImageField(upload_to='images', verbose_name="Header Image", help_text="select a header image for your profile page", default=None, null=True, blank=True)
    color = models.CharField(max_length=7, verbose_name="Color", help_text="select a color to be used in your profile page", default="#5a5c69", null=True, blank=True)
    is_public = models.BooleanField(default=False, verbose_name="Should your profile be visible for others?", help_text="Others can then see your Profile page as you can see it.")
    about_me = models.TextField(default="", verbose_name="About Me", help_text="Tell us something about yourself!", null=True, blank=True)

    pinterest = models.URLField(default="", verbose_name="Pinterest", help_text="insert your pinterest profile URL", null=True, blank=True)
    spotify = models.URLField(default="", verbose_name="Spotify", help_text="insert your spotify profile URL", null=True, blank=True)
    instagram = models.URLField(default="", verbose_name="Instagram", help_text="insert your instagram profile URL", null=True, blank=True)
    twitter = models.URLField(default="", verbose_name="Twitter", help_text="insert your twitter profile URL", null=True, blank=True)
    goodreads = models.URLField(default="", verbose_name="Goodreads", help_text="insert your goodreads profile URL", null=True, blank=True)
    nanowrimo = models.URLField(default="", verbose_name="NaNoWriMo.org", help_text="insert your nanowrimo.org profile URL", null=True, blank=True)

    daily_goal = models.IntegerField(null=True, verbose_name="Daily Goal", help_text="set a daily goal you want to reach", blank=True)
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
        blank=True,
        verbose_name="Goal Unit", help_text="in which unit do you want to measure your daily goal?"
    )

    def __str__(self):
        return self.user.username


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', verbose_name="Project", help_text="for which project do you want to save a log?", on_delete=models.CASCADE)
    date = models.DateField(default="", verbose_name="Date", help_text="insert the date of your log (YYYY-MM-DD)")
    time = models.TimeField(default="", verbose_name="Time", help_text="give your log a time (HH:MM:SS)")
    count = models.IntegerField(verbose_name="Count", help_text="what is your progress?")
    note = models.TextField(null=True, blank=True, verbose_name="Note", help_text="do you want to comment your log?")
    is_update = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return str("{0} ({1} {2})".format(self.project, self.date, self.time))


class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name="Title", help_text="give your project a name", default="")
    subtitle = models.CharField(max_length=300, verbose_name="Subtitle", help_text="does your project has a subtitle?", default="", null=True, blank=True)
    slug = models.SlugField(default="")
    created_at = models.DateTimeField(default="")
    goal = models.IntegerField(default=50000, verbose_name="Goal", help_text="which goal do you want to reach?")
    deadline = models.DateField(default="", verbose_name="Deadline", help_text="do you have a deadline? (YYYY-MM-DD)", null=True, blank=True)
    topic = models.CharField(max_length=200, verbose_name="Topic", help_text="write things like genre, tags, ...", default="", null=True, blank=True)
    synopsis = models.TextField(default="", verbose_name="Synopsis", help_text="what is your project about?", null=True, blank=True)
    excerpt = models.TextField(default="", verbose_name="Excerpt", help_text="give an example of your work", null=True, blank=True)
    pinterest = models.URLField(default="", verbose_name="Pinterest", help_text="insert URL of pinterest board", null=True, blank=True)
    spotify = models.URLField(default="", verbose_name="Spotify", help_text="insert URL of spotify playlist", null=True, blank=True)
    image = models.ImageField(upload_to='images', verbose_name="Image", help_text="give your project cover image", default=None, null=True, blank=True)
    color = models.CharField(max_length=7, verbose_name="Color", help_text="select a color (please use hexadecimal html codation, e.g. #00ff00)", default="#6f42c1", null=True, blank=True)
    is_public = models.BooleanField(default=False, verbose_name="Should your project be visible to other users?", help_text="Other users then can see cover, description texts and links")
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
    priority = models.IntegerField(choices=PRIORITY, verbose_name="Priority", help_text="which priority does your project have?", default=5)
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
        verbose_name="Status", help_text="what is the status of your project?"
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
        verbose_name="Unit", help_text="in which unit do you want to measure your progress?"
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
        verbose_name="Type", help_text="what kind of project is your project?"
    )

    def __str__(self):
        return self.title
