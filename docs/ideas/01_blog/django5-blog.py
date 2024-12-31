"""
# Project Structure
blog_project/
    ├── manage.py
    ├── requirements.txt
    ├── .env
    ├── blog/                      # Main project directory
    │   ├── __init__.py
    │   ├── settings/             # Split settings
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── development.py
    │   │   └── production.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py              # For async support
    │
    ├── core/                    # Core app for shared functionality
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── utils.py
    │   └── templatetags/
    │
    ├── accounts/               # User management app
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── urls.py
    │   ├── views.py
    │   └── templates/
    │       └── accounts/
    │
    ├── posts/                  # Blog posts app
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── api/               # API endpoints
    │   │   ├── __init__.py
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   └── templates/
    │       └── posts/
    │
    ├── comments/              # Comments app
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── urls.py
    │   ├── views.py
    │   └── templates/
    │       └── comments/
    │
    ├── analytics/            # Analytics app
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── urls.py
    │   └── views.py
    │
    ├── static/              # Static files
    │   ├── css/
    │   ├── js/
    │   └── images/
    │
    ├── media/              # User uploaded content
    │
    └── templates/         # Global templates
        ├── base.html
        ├── navbar.html
        └── includes/
"""
# Key Components Implementation

# 1. Models (posts/models.py)
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from enum import Enum

User = get_user_model()

class PostStatus(Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True)
    status = models.CharField(
        max_length=20,
        choices=PostStatus,  # Django 5 feature: direct enum usage
        default=PostStatus.DRAFT
    )
    categories = models.ManyToManyField(Category)
    tags = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True,
        db_generated=models.DatabaseGeneratedField(  # Django 5 feature
            expression='NOW()'
        )
    )
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['status', '-created']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:post_detail', args=[self.slug])

# 2. Forms (posts/forms.py)
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'featured_image', 'status', 'categories', 'tags']
        
        # Django 5 feature: field groups
        field_groups = {
            'basic_info': {
                'fields': ['title', 'content'],
                'template_name': 'forms/post_basic_info.html'
            },
            'metadata': {
                'fields': ['status', 'categories', 'tags'],
                'template_name': 'forms/post_metadata.html'
            }
        }

# 3. Views (posts/views.py)
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(status=PostStatus.PUBLISHED)
        if 'category' in self.kwargs:
            queryset = queryset.filter(categories__slug=self.kwargs['category'])
        return queryset

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'

    async def get_object(self):  # Django 5 feature: async view
        post = await super().get_object()
        # Increment views count atomically
        await Post.objects.filter(pk=post.pk).aupdate(
            views_count=F('views_count') + 1
        )
        return post

# 4. Admin (posts/admin.py)
from django.contrib import admin
from .models import Post, Category

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created']
    list_filter = ['status', 'created', 'categories']
    faceted_filters = ['status', 'categories']  # Django 5 feature
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created'

# 5. URLs (posts/urls.py)
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category>/', views.PostListView.as_view(), name='post_by_category'),
]

# 6. Templates (templates/posts/post_list.html)
"""
{% extends 'base.html' %}

{% block content %}
    <div class="container mx-auto px-4">
        <h1 class="text-3xl font-bold mb-6">Blog Posts</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for post in posts %}
                <article class="bg-white rounded-lg shadow-md overflow-hidden">
                    {% if post.featured_image %}
                        <img src="{{ post.featured_image.url }}" alt="{{ post.title }}" class="w-full h-48 object-cover">
                    {% endif %}
                    
                    <div class="p-6">
                        <h2 class="text-xl font-semibold mb-2">
                            <a href="{{ post.get_absolute_url }}" class="hover:text-blue-600">
                                {{ post.title }}
                            </a>
                        </h2>
                        
                        <div class="text-gray-600 text-sm mb-4">
                            {{ post.created|date:"F j, Y" }} by {{ post.author.get_full_name }}
                        </div>
                        
                        <p class="text-gray-700 mb-4">
                            {{ post.content|truncatewords:30 }}
                        </p>
                        
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-500">
                                {{ post.views_count }} views
                            </span>
                            <a href="{{ post.get_absolute_url }}" 
                               class="text-blue-600 hover:text-blue-800">
                                Read more →
                            </a>
                        </div>
                    </div>
                </article>
            {% endfor %}
        </div>
        
        {% include "includes/pagination.html" %}
    </div>
{% endblock %}
"""

# 7. Settings (blog/settings/base.py)
"""
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'taggit',
    
    # Local apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'posts.apps.PostsConfig',
    'comments.apps.CommentsConfig',
    'analytics.apps.AnalyticsConfig',
]

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Media and Static files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
"""
