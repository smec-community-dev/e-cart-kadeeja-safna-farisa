from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect

@receiver(user_logged_in)
def redirect_after_google_login(sender, request, user, **kwargs):
    """
    Redirect users based on type AFTER social login (Google)
    """
    # If the login came from manual login view, do nothing.
    if request.resolver_match.url_name == "login":
        return

    # Google login redirection
    if user.is_buyer:
        request.session["redirect_to"] = "userapp:index"
    elif user.is_seller:
        request.session["redirect_to"] = "sellerapp:index"
    elif user.is_admin:
        request.session["redirect_to"] = "adminapp:index"
