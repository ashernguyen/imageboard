from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator, URLValidator

import os

from . import validators

# Only technical admins can change data of these models

class User(models.Model):
    DEFAULT_GROUP = UserGroup.objects.get(name='User')
    
    name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    pass_hash = models.CharField(max_length=100)
    pass_salt = models.CharField(max_length=100)
    pass_algo = models.CharField(choices=[])
    group = models.ForeignKey('UserGroup', on_delete=models.SET_DEFAULT, related_name='user_groups', default=DEFAULT_GROUP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    priveleges = models.ManyToManyField('Privelege', related_name='priveleges', null=True, blank=True)

    def __name__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.name == 'User':
            raise Exception('Cannot delete User group!')
        super().delete(*args, **kwargs)

class Privelege(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# Public models

class Board(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbr = models.CharField(max_length=10, unique=True, validators=[validators.abbr_validator])
    description = models.TextField(blank=True)
    bump_limit = models.IntegerField(default=500)
    spam_words = models.CharField(blank=True, validators=[validators.csv_validator])
    picture = models.ImageField(upload_to="board_avas/", null=True, blank=True, validators=[validators.ava_validator])
    author = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.abbr + ' : ' + self.name

class Thread(models.Model):
    sticked = models.BooleanField(default=False)
    read_only = models.BooleanField(default=False)
    first_post = models.OneToOneField('Post', on_delete=models.CASCADE, related_name='first_post', null=True, blank=True)
    board = models.ForeignKey('Board', on_delete=models.CASCADE, related_name='boards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posts_count = models.IntegerField(default=0)

    def __str__(self):
        if self.first_post is not None:
            return str(self.first_post)
        else:
            return str(self.id)

    def has_bump_limit(self):
        return self.posts_count >= self.board.bump_limit

class Post(models.Model):
    title = models.CharField(max_length=200, blank=True)
    author = models.CharField(max_length=50, blank=True)
    contact = models.CharField(max_length=100, blank=True, validators=[EmailValidator, URLValidator])
    options = models.CharField(blank=True, validators=[validators.csv_validator])
    message = models.TextField(max_length=15000)
    poster_ip = models.GenericIPAddressField()
    thread = models.ForeignKey('Thread', on_delete=models.CASCADE, related_name="threads")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.poster_ip + ' : ' + self.message[:20]

    def save(self, *args, **kwargs):
        if self.thread.first_post is None:
            self.thread.first_post = self
        self.thread.posts_count += 1
        super().save(*args, **kwargs)   

class PostFile(models.Model):
    ALLOWED_EXTENSIONS = [
        'jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm', 'pdf', 'djvu', 'mp3', 'ogg'
    ]
    
    post_file = models.FileField(upload_to="post_files/", validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)])
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return os.path.basename(self.post_file.name) + ' : (' + str(self.post) + ')'

class Report(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="posts")
    reason = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '(' + str(self.post) + ') : ' + self.reason[:20] 

class Ban(models.Model):
    poster_ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField()
    reason = models.TextField(max_length=200)
    board = models.ForeignKey('Board', on_delete=models.CASCADE, related_name="boards", null=True, blank=True)

    def __str__(self):
        board = ''
        if self.board is not None:
            board = '(' + str(self.board) + ')'
        return board + ' : ' self.poster_ip + ' : ' + self.reason[:20]


