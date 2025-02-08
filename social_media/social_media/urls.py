import allauth
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Connectly.views import welcome
from allauth.socialaccount.views import login_cancelled, login_error
from allauth.socialaccount.providers.google.views import oauth2_login, oauth2_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Connectly.urls')),
    path('accounts/google/login/', oauth2_login, name='google_login'),
    path('accounts/google/login/callback/', oauth2_callback, name='google_callback'),
    path('accounts/social/login/cancelled/', login_cancelled, name='account_login_cancelled'),
    path('accounts/social/login/error/', login_error, name='account_login_error'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
