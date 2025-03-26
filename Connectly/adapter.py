#adapter for google login, sign up
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            return
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return
        try:
            user = User.objects.get(email=email)
            if not sociallogin.is_existing:
                sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def is_open_for_signup(self, request, sociallogin):
        return True

    def get_signup_redirect_url(self, request, sociallogin):
        return reverse("socialaccount_signup")

    def get_login_redirect_url(self, request):
        return reverse("home")
