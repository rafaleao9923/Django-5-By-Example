# Changes from Chapter02 to Chapter03

## New Features Added
- Tagging system for blog posts
- Full-text search functionality
- RSS feed for latest posts
- Sitemap for SEO optimization

## Model Changes
- Added TaggableManager to Post model for tagging
- Added tag relationship fields and methods

## View Changes
- Added post_search view for full-text search
- Enhanced post_list to handle tag filtering
- Added similar posts recommendation in post_detail
- Added tag parameter handling in post_list

## URL Changes
- Added new URL patterns:
  * /tag/<slug:tag_slug>/ - for tag filtering
  * /feed/ - for RSS feed
  * /search/ - for search functionality

## New Files
- feeds.py containing:
  * LatestPostsFeed class for RSS feed
- sitemaps.py containing:
  * PostSitemap class for SEO sitemap
- templatetags/ directory for custom template tags

## Form Changes
- Added SearchForm for search functionality

## Template Changes
- Added tag display and filtering in templates
- Added search form in templates
- Added RSS feed link in templates
- Added similar posts section in post detail

## Dependencies Added
- django-taggit for tagging
- Markdown for content formatting
- psycopg for PostgreSQL support

## Configuration Changes
- Added PostgreSQL database configuration
- Added email configuration for production
