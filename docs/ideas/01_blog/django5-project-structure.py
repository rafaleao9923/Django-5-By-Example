# Django 5 Project Structure
myproject/
    ├── manage.py                  # Project management script
    ├── pyproject.toml            # Project dependencies and settings (new in Django 5)
    ├── requirements/
    │   ├── base.txt              # Base requirements
    │   ├── local.txt             # Local development requirements
    │   └── production.txt        # Production requirements
    │
    ├── config/                   # Project configuration directory
    │   ├── __init__.py
    │   ├── asgi.py              # ASGI configuration (for async)
    │   ├── wsgi.py              # WSGI configuration
    │   ├── urls.py              # Main URL configuration
    │   └── settings/            # Split settings configuration
    │       ├── __init__.py
    │       ├── base.py
    │       ├── local.py
    │       └── production.py
    │
    ├── apps/                    # Application directory
    │   ├── __init__.py
    │   ├── core/               # Core application
    │   │   ├── __init__.py
    │   │   ├── apps.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   │
    │   └── users/             # Users application
    │       ├── __init__.py
    │       ├── admin.py
    │       ├── apps.py
    │       ├── forms.py
    │       ├── managers.py
    │       ├── models.py
    │       ├── urls.py
    │       └── views.py
    │
    ├── static/                # Static files
    ├── media/                 # User-uploaded files
    ├── templates/             # Global templates
    ├── locale/                # Translations
    └── docs/                  # Project documentation

# 1. Project Configuration (pyproject.toml)
[project]
name = "myproject"
version = "1.0.0"
description = "My Django 5 Project"
dependencies = [
    "Django>=5.0",
    "psycopg>=3.0",
    "redis>=5.0",
    "celery>=5.3",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py", "*_test.py"]

[tool.black]
line-length = 88
include = '\.pyi?$'

# 2. Core Application Configuration (apps/core/apps.py)
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
    
    def ready(self):
        """Initialize application settings and signals."""
        from django.conf import settings
        # Register signals
        import apps.core.signals
        
        # Initialize app-specific settings
        if not hasattr(settings, 'CORE_SETTINGS'):
            settings.CORE_SETTINGS = {
                'DEFAULT_TIMEOUT': 300,
                'MAX_RETRIES': 3,
            }

# 3. Application Factory (apps/core/factories.py)
from django.apps import apps
from django.conf import settings
from importlib import import_module

class ApplicationFactory:
    """Factory for dynamic application loading and configuration."""
    
    @classmethod
    def create_app(cls, app_name, **kwargs):
        """Create and configure a Django application."""
        app_config = {
            'name': f'apps.{app_name}',
            'verbose_name': kwargs.get('verbose_name', app_name.title()),
            'default_auto_field': kwargs.get(
                'default_auto_field', 
                'django.db.models.BigAutoField'
            ),
        }
        
        # Create AppConfig instance
        app_config_cls = type(
            f'{app_name.title()}Config',
            (AppConfig,),
            app_config
        )
        
        # Register app with Django
        apps.register_config(app_config_cls(app_name))
        
        return app_config_cls

# 4. Application Registry (apps/core/registry.py)
from django.apps import apps
from django.conf import settings

class ApplicationRegistry:
    """Registry for managing application metadata and relationships."""
    
    def __init__(self):
        self._registry = {}
        self._dependencies = {}
    
    def register(self, app_name, dependencies=None):
        """Register an application and its dependencies."""
        if dependencies is None:
            dependencies = []
            
        if app_name in self._registry:
            raise ValueError(f'Application {app_name} already registered')
            
        self._registry[app_name] = {
            'config': apps.get_app_config(app_name),
            'dependencies': dependencies
        }
        self._dependencies[app_name] = dependencies
        
    def get_app(self, app_name):
        """Get application configuration."""
        return self._registry.get(app_name)
        
    def get_dependencies(self, app_name):
        """Get application dependencies."""
        return self._dependencies.get(app_name, [])
        
    def check_dependencies(self):
        """Check if all application dependencies are met."""
        for app_name, deps in self._dependencies.items():
            for dep in deps:
                if dep not in self._registry:
                    raise ValueError(
                        f'Dependency {dep} for {app_name} not registered'
                    )

# 5. Application URLs Configuration (apps/users/urls.py)
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path(
        'register/',
        views.RegisterView.as_view(),
        name='register'
    ),
    path(
        'profile/',
        views.ProfileView.as_view(),
        name='profile'
    ),
]

# 6. Application Models (apps/users/models.py)
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model with additional fields."""
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

# 7. Application Views (apps/users/views.py)
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import UserRegistrationForm, UserProfileForm

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    
    async def form_valid(self, form):  # Django 5 async view
        user = await form.save(commit=False)
        # Additional async processing
        await user.asave()
        return super().form_valid(form)

# 8. Application Forms (apps/users/forms.py)
from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
        # Django 5 field groups feature
        field_groups = {
            'credentials': {
                'fields': ['username', 'password'],
                'template_name': 'users/field_groups/credentials.html'
            },
            'profile': {
                'fields': ['email'],
                'template_name': 'users/field_groups/profile.html'
            }
        }

# 9. Project Settings Integration
# config/settings/base.py

from pathlib import Path
import sys

# Add apps directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / 'apps'))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Local apps
    'apps.core.apps.CoreConfig',
    'apps.users.apps.UsersConfig',
]

# Application-specific settings
AUTH_USER_MODEL = 'users.User'

# Register applications with custom registry
from apps.core.registry import ApplicationRegistry
app_registry = ApplicationRegistry()

app_registry.register('core')
app_registry.register('users', dependencies=['core'])
app_registry.check_dependencies()

# 10. Application Management Commands
# apps/core/management/commands/create_app.py
from django.core.management.base import BaseCommand
from apps.core.factories import ApplicationFactory

class Command(BaseCommand):
    help = 'Create a new Django application'
    
    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str)
        parser.add_argument(
            '--verbose-name',
            type=str,
            help='Verbose name for the application'
        )
    
    def handle(self, *args, **options):
        app_name = options['app_name']
        verbose_name = options.get('verbose_name')
        
        try:
            ApplicationFactory.create_app(
                app_name,
                verbose_name=verbose_name
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created app "{app_name}"')
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error creating app: {str(e)}')
            )

# Usage:
# python manage.py create_app blog --verbose-name="Blog System"
