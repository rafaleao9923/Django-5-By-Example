# Changes from Chapter01 to Chapter02

## New Features Added
- Comment system for blog posts
- Email sharing functionality
- Pagination for post lists
- Class-based views (PostListView)
- Date-based URL patterns for posts

## Model Changes
- Added Comment model with fields:
  * post (ForeignKey to Post)
  * name
  * email
  * body
  * created/updated timestamps
  * active status
- Enhanced Post model:
  * Added unique_for_date constraint on slug field
  * Added get_absolute_url method
  * Added related_name 'comments' for comment relationship

## View Changes
- Added new view functions:
  * post_share - handles email sharing
  * post_comment - handles comment submission
- Enhanced existing views:
  * post_list - added pagination
  * post_detail - added comment form handling
- Added PostListView class-based view

## URL Changes
- Changed from ID-based to date-based URLs:
  * Old: /<int:id>/
  * New: /<int:year>/<int:month>/<int:day>/<slug:post>/
- Added new URL patterns:
  * /<int:post_id>/share/
  * /<int:post_id>/comment/

## Admin Changes
- Added CommentAdmin for managing comments
- Enhanced PostAdmin with additional configuration

## New Files
- forms.py containing:
  * EmailPostForm
  * CommentForm
