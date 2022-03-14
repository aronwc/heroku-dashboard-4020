from django.urls import path
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path("graph/", views.plot, name="graph"),
    path('pretrial/', views.pretrial, name='pretrial'),
    path('display/', views.display, name='display'),
    path('get-topics-ajax/', views.get_topics_ajax, name="get_topics_ajax"),
]