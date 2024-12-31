# 1. Facet Filters in Admin
from django.contrib import admin
from .models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'author']
    list_filter = ['status', 'author']
    
    # Enable facet counts for status filter
    faceted_filters = ['status']

admin.site.register(Article, ArticleAdmin)

# 2. Simplified Form Field Rendering
# forms.py
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        
        # New field groups feature
        field_groups = {
            'user_info': {
                'fields': ['name', 'email'],
                'template_name': 'forms/user_info_group.html'
            },
            'content': {
                'fields': ['body'],
                'template_name': 'forms/content_group.html'
            }
        }

# Template example (forms/user_info_group.html)
"""
<div class="user-info-group">
    {% for field in fields %}
        <div class="form-group">
            {{ field.label_tag }}
            {{ field }}
            {% if field.help_text %}
                <small class="help-text">{{ field.help_text }}</small>
            {% endif %}
            {{ field.errors }}
        </div>
    {% endfor %}
</div>
"""

# 3. Database-computed Default Values
from django.db import models
from django.db.models import F
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=200)
    created = models.DateTimeField(default=timezone.now)
    # New database-computed default
    last_modified = models.DateTimeField(
        default=models.DatabaseDefault(timezone.now),
        editable=False
    )

# 4. Database-generated Model Fields
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Database-generated field
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_generated=models.DatabaseGeneratedField(
            expression=F('price') * (1 + F('tax_rate') / 100)
        )
    )

# 5. Enhanced Model Field Choices
from enum import Enum

class PostStatus(Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'

class Post(models.Model):
    title = models.CharField(max_length=200)
    # New way to declare choices directly with enum
    status = models.CharField(
        max_length=20,
        choices=PostStatus,  # Direct enum usage without .choices
        default=PostStatus.DRAFT
    )

# 6. Async Features
from django.contrib.auth.decorators import async_login_required
from django.core.signals import request_finished
from django.dispatch import receiver

# Async login required decorator
@async_login_required
async def my_async_view(request):
    # Async view logic here
    result = await some_async_operation()
    return HttpResponse(result)

# Async signal handling
@receiver(request_finished, dispatch_async=True)
async def my_async_callback(sender, **kwargs):
    await some_async_cleanup()

# Async authentication
from django.contrib.auth import get_user_model
User = get_user_model()

async def get_user_data(request):
    user = await User.objects.aget(username=request.user.username)
    related_data = await user.profile.aget()
    return related_data

# Async ORM operations
async def list_articles():
    async for article in Article.objects.filter(status='published'):
        print(article.title)
    
    # Bulk async operations
    articles = [article async for article in Article.objects.all()]
    count = await Article.objects.acount()
    exists = await Article.objects.filter(status='draft').aexists()
