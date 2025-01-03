# Chapter 5 Changes

## Docker Configuration Updates
- Updated Dockerfile to use Python 3.12.3-slim
- Added psycopg[binary] installation for PostgreSQL support
- Modified docker-compose.yml to include:
  - web_migrate service for database migrations
  - web_run service with port mapping
  - Dependency chain between services

## New Dependencies
- Added social authentication packages:
  - social-auth-app-django==5.4.0
- Added development utilities:
  - django-extensions==3.2.3
  - werkzeug==3.0.2
  - pyOpenSSL==24.1.0

## Shell Script Enhancements
- Added new commands to do.sh:
  - migrate: Apply Django migrations
  - makemigrations: Create new migrations
  - check: Validate Django settings
  - shell: Open bash terminal in web_run container

## Code Formatting
- Standardized string quotes in manage.py
- Improved error message formatting

## Architectural Changes
- Added support for PostgreSQL database
- Prepared infrastructure for social authentication
- Added development debugging tools
