from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='homepage'),
    path("graph/", views.homepage, name="graph"),
]