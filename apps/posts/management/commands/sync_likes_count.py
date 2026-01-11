"""
Management command to sync Post.likes_count from actual Like rows.

This command recalculates and updates Post.likes_count by counting
the actual Like objects for each post. It's safe to run multiple times
and can be used to fix inconsistencies caused by unexpected errors,
manual database edits, or bulk operations.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from apps.posts.models import Post


class Command(BaseCommand):
    help = 'Recalculate and sync Post.likes_count from actual Like rows'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of posts to update in each batch (default: 1000)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        verbose = options['verbose']
        
        self.stdout.write('Starting likes_count sync...')
        
        # Get all posts with their actual like counts
        posts_with_counts = (
            Post.objects
            .annotate(actual_likes_count=Count('likes'))
            .values('id', 'likes_count', 'actual_likes_count')
        )
        
        total_posts = posts_with_counts.count()
        self.stdout.write(f'Found {total_posts} posts to check')
        
        if total_posts == 0:
            self.stdout.write(self.style.SUCCESS('No posts found. Nothing to sync.'))
            return
        
        # Filter posts that need updating
        posts_to_update = [
            post for post in posts_with_counts
            if post['likes_count'] != post['actual_likes_count']
        ]
        
        posts_needing_update = len(posts_to_update)
        self.stdout.write(f'Found {posts_needing_update} posts with mismatched likes_count')
        
        if posts_needing_update == 0:
            self.stdout.write(self.style.SUCCESS('All posts have correct likes_count. Nothing to update.'))
            return
        
        # Update posts in batches atomically
        updated_count = 0
        for i in range(0, posts_needing_update, batch_size):
            batch = posts_to_update[i:i + batch_size]
            post_ids = [post['id'] for post in batch]
            
            with transaction.atomic():
                # Create a mapping of post_id to actual_likes_count
                post_updates = {
                    post['id']: post['actual_likes_count']
                    for post in batch
                }
                
                # Bulk update posts
                posts_to_bulk_update = []
                for post_id, actual_count in post_updates.items():
                    post = Post.objects.get(pk=post_id)
                    post.likes_count = actual_count
                    posts_to_bulk_update.append(post)
                
                Post.objects.bulk_update(
                    posts_to_bulk_update,
                    ['likes_count'],
                    batch_size=batch_size
                )
                
                updated_count += len(posts_to_bulk_update)
                
                if verbose:
                    for post_id, actual_count in post_updates.items():
                        old_count = next(
                            p['likes_count'] for p in batch
                            if p['id'] == post_id
                        )
                        self.stdout.write(
                            f'  Post {post_id}: {old_count} -> {actual_count} likes'
                        )
            
            self.stdout.write(
                f'Updated batch {i // batch_size + 1}: '
                f'{updated_count}/{posts_needing_update} posts'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synced likes_count for {updated_count} posts'
            )
        )
