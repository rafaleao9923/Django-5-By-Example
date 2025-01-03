from django.core.management.base import BaseCommand
from blog.models import Post
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a new blog post'

    def add_arguments(self, parser):
        parser.add_argument('title', type=str, help='Title of the post')
        parser.add_argument('body', type=str, help='Body content of the post')
        parser.add_argument('author', type=str, help='Username of the author')

    def handle(self, *args, **kwargs):
        title = kwargs['title']
        body = kwargs['body']
        author_username = kwargs['author']
        
        try:
            author = User.objects.get(username=author_username)
            from django.utils.text import slugify
            post = Post.objects.create(
                title=title,
                slug=slugify(title),
                body=body,
                author=author,
                status=Post.Status.PUBLISHED
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created post: {post.title}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {author_username} does not exist'))
