from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from CoreApp.models import User


@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    """
    Signal triggered after a new user is registered
    """
    if created:
        # Send welcome email
        try:
            send_mail(
                'Welcome to Our E-commerce Site!',
                f'''
                Hello {instance.username},

                Thank you for registering with us!

                Your account details:
                - Username: {instance.username}
                - Email: {instance.email}
                - Account Type: {'Buyer' if instance.is_buyer else 'Seller' if instance.is_seller else 'Admin'}

                We're excited to have you on board!

                Best regards,
                The E-commerce Team
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send welcome email: {e}")

        # Log registration
        print(f"New user registered: {instance.username} ({instance.email})")


@receiver(user_logged_in)
def handle_post_login(sender, request, user, **kwargs):
    """
    Signal triggered after user login - handles redirect logic
    """
    # Set session variables for user type
    request.session['user_type'] = 'buyer'  # default
    if user.is_admin:
        request.session['user_type'] = 'admin'
    elif user.is_seller:
        request.session['user_type'] = 'seller'

    # Store user info in session
    request.session['user_email'] = user.email
    request.session['username'] = user.username

    print(f"User {user.username} logged in as {request.session['user_type']}")


@receiver(user_logged_out)
def handle_post_logout(sender, request, user, **kwargs):
    """
    Signal triggered after user logout
    """
    if user:
        print(f"User {user.username} logged out")

    # Clear session data
    if 'user_type' in request.session:
        del request.session['user_type']