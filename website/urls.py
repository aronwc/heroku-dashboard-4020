from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path("firsttest", views.plot, name="dashboard"),
    path("test", views.test, name="dashboard"),
    path("", views.psql, name="Query")
    #path("upload-csv/", views.psql, name="responses_test"),
]