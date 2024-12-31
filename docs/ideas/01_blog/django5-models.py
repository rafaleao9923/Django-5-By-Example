# 1. Basic Model Structure with Django 5 Features
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import F, Q
from enum import Enum
from datetime import datetime

# Post Status Enum
class PostStatus(Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class Meta:
        verbose_name_plural = 'categories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name', 'slug'])
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# 2. Advanced Model with Django 5's New Features
class Post(models.Model):
    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    
    # Author relationship
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    # Using Enum directly for choices (Django 5 feature)
    status = models.CharField(
        max_length=20,
        choices=PostStatus,  # Direct enum usage
        default=PostStatus.DRAFT
    )
    
    # Categories and Tags
    categories = models.ManyToManyField(Category, related_name='posts')
    tags = models.JSONField(default=list)
    
    # Timestamps with database-computed fields (Django 5 feature)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        db_generated=models.DatabaseGeneratedField(
            expression='CURRENT_TIMESTAMP'
        )
    )
    
    # Database-computed word count (Django 5 feature)
    word_count = models.IntegerField(
        db_generated=models.DatabaseGeneratedField(
            expression="length(regexp_replace(content, '[\\s]+', ' ', 'g')) - length(replace(regexp_replace(content, '[\\s]+', ' ', 'g'), ' ', '')) + 1"
        )
    )
    
    # Metrics
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(word_count__gte=0),
                name='non_negative_word_count'
            )
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

# 3. Comment Model with Threaded Structure
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author', 'created_at'])
        ]

# 4. User Profile with Custom Fields
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    website = models.URLField(blank=True)
    
    # Social media links as JSON
    social_links = models.JSONField(
        default=dict,
        help_text='Social media profile links'
    )
    
    # Preferences with constraints
    notification_preferences = models.JSONField(
        default=dict,
        validators=[
            validate_notification_preferences
        ]
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['user'])
        ]

# 5. Tag Model with Metrics
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    # Auto-updated usage count (Django 5 feature)
    usage_count = models.IntegerField(
        db_generated=models.DatabaseGeneratedField(
            expression='(SELECT COUNT(*) FROM posts_post_tags WHERE tag_id = id)'
        )
    )
    
    class Meta:
        ordering = ['-usage_count']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-usage_count'])
        ]

# 6. Media Model for Post Attachments
class PostMedia(models.Model):
    class MediaType(Enum):
        IMAGE = 'image'
        VIDEO = 'video'
        DOCUMENT = 'document'
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media'
    )
    file = models.FileField(upload_to='post_media/%Y/%m/')
    media_type = models.CharField(
        max_length=20,
        choices=MediaType
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Auto-generated metadata (Django 5 feature)
    file_size = models.PositiveIntegerField(
        db_generated=models.DatabaseGeneratedField(
            expression='length(file)'
        )
    )
    
    class Meta:
        verbose_name_plural = 'media'
        indexes = [
            models.Index(fields=['post', 'media_type'])
        ]

# 7. Custom Model Managers
class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def published(self):
        return self.get_queryset().filter(
            status=PostStatus.PUBLISHED
        )
    
    async def apublished(self):  # Django 5 async manager method
        return await self.get_queryset().filter(
            status=PostStatus.PUBLISHED
        ).aiterator()

# 8. Model Mixins
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class MetadataMixin(models.Model):
    metadata = models.JSONField(default=dict)
    
    class Meta:
        abstract = True

# 9. Model Validators
def validate_notification_preferences(value):
    required_keys = {'email', 'push', 'site'}
    if not all(key in value for key in required_keys):
        raise ValidationError(
            f'Missing required preferences: {required_keys}'
        )

# 10. Model Signals
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Post)
async def update_post_metrics(sender, instance, created, **kwargs):
    if created:
        # Async update of related metrics
        await PostMetrics.objects.acreate(
            post=instance,
            initial_word_count=instance.word_count
        )
