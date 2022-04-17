from django.urls import path, include

from django.contrib import admin
from django.contrib.auth import views as auth_views
#from django.views.generic.base import RedirectView 

admin.autodiscover()

import website.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", include('website.urls')),
    #path("", lambda x: HttpResponseRedirect('/admin/')),
    path("admin/", admin.site.urls),
    #path('accounts/login/', auth_views.LoginView.my_view(), name="login"),
]
