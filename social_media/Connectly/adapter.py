from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        This method is called just after a successful authentication from the social provider,
        but before the login is actually processed.
        If a user with the same email already exists, connect the social account to the existing user.
        """
        # If the user is already logged in, do nothing.
        if request.user.is_authenticated:
            return

        # Get the email from the social account data.
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return  # No email available—continue with the normal flow

        try:
            # Look for an existing user with this email.
            user = User.objects.get(email=email)
            # If found and the social account is not already linked, connect it.
            if not sociallogin.is_existing:
                sociallogin.connect(request, user)
        except User.DoesNotExist:
            # No user with this email exists, so proceed with the signup flow.
            pass

    def is_open_for_signup(self, request, sociallogin):
        """
        Always allow signups. For new users, this method will return True,
        so the signup form is presented. For existing users, the pre_social_login
        method connects the account so that the signup form is skipped.
        """
        return True

    def get_signup_redirect_url(self, request, sociallogin):
        """
        For new users, this URL is used to redirect to your custom signup form.
        (It should be set up in your urls.py with the name "socialaccount_signup".)
        """
        return reverse("socialaccount_signup")

    def get_login_redirect_url(self, request):
        """
        After login (whether via social or regular auth), redirect the user here.
        """
        return reverse("home")
