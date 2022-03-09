from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path("", views.plot, name="dashboard"),
    path("test", views.test, name="dashboard"),
    #path("upload-csv/", views.psql, name="responses_test"),
]