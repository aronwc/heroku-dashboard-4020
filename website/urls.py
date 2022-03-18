from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'website'
urlpatterns = [


    path('', views.index, name='index'),
    path("graph/", views.plot, name="graph"),
    path('pretrial/', views.pretrial, name='pretrial'),
    path('display/', views.display, name='display'),
    path('get-questions-ajax/', views.get_questions_ajax, name="get_questions_ajax"),
    path('get-years-ajax/', views.get_years_ajax, name="get_years_ajax"),
    path('bennett-bokeh/', views.bennett_bokeh, name="bennett_bokeh"),
    #path('', views.index, name='index'),
    path("firsttest", views.plot, name="dashboard"),
    path("test", views.test, name="dashboard"),
    path("", views.psql, name="Query"),

    path("pretrial", views.pretrial, name='pretrial')

    #path("upload-csv/", views.psql, name="responses_test"),

]

urlpatterns += staticfiles_urlpatterns()