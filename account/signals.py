from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import *
import cloudinary.uploader


#TODO: for profile
@receiver(post_delete, sender=Profile)
def delete_profile_picture_on_profile_delete(sender, instance, **kwargs):
    """Delete profile picture when Profile is deleted."""
    if instance.profile_picture:
        public_id = instance.profile_picture.public_id
        if public_id:
            cloudinary.uploader.destroy(public_id)

@receiver(pre_save, sender=Profile)
def delete_old_profile_picture_on_update(sender, instance, **kwargs):
    """Delete old profile picture when updating Profile."""
    if not instance.pk:
        return

    try:
        old_profile = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return

    if old_profile.profile_picture and str(old_profile.profile_picture) != str(instance.profile_picture):
        print(f"old {old_profile.profile_picture} new {instance.profile_picture}")
        public_id = old_profile.profile_picture.public_id
        if public_id:
            cloudinary.uploader.destroy(public_id)


#TODO: for post

@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if instance.post_image:
        # Extract the public ID of the Cloudinary image
        public_id = instance.post_image.public_id
        if public_id:
            # Delete the image from Cloudinary
            cloudinary.uploader.destroy(public_id)
            
            
@receiver(post_delete, sender=Profile)
def delete_author_posts_images(sender, instance, **kwargs):
    """Delete all posts and their Cloudinary images when an author (Profile) is deleted."""
    posts = Post.objects.filter(author=instance)
    for post in posts:
        if post.post_image:
            public_id = post.post_image.public_id
            if public_id:
                cloudinary.uploader.destroy(public_id)