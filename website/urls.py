from django.urls import path
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path("graph/", views.plot, name="graph")
    path('<int:question_id>/', views.pretrial, name='pretrial')
]