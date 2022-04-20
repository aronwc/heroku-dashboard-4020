from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'website'
urlpatterns = [


    path('', views.survey_dashboard, name='survey_dashboard'),
    path('pretrial/', views.pretrial, name='pretrial'),
    path('survey-dashboard/', views.survey_dashboard, name='survey_dashboard'),
    path('dockets-dashboard/', views.dockets_dashboard, name='dockets_dashboard'),
    path('get-questions-ajax/', views.get_questions_ajax, name="get_questions_ajax"),
    path('get-years-ajax/', views.get_years_ajax, name="get_years_ajax"),
    path('generate-panel-2-options/', views.generate_panel_2_options, name="generate_panel_2_options"),
    path('get-graphs-ajax/', views.get_graphs_ajax, name="get_graphs_ajax"),
    path('bennett-bokeh/', views.bennett_bokeh, name="bennett_bokeh"),
    path('process-generate/', views.process_generate, name="process_generate"),
    path('stack-group-bar-chart/', views.stack_group_bar_chart, name="stack_group_bar_chart"),
    path('get-docket-charge-by-mag-num/', views.SearchResultsList.as_view(), name="get_docket_charge_by_mag_num"),
    path("dockets", views.psql, name="dockets_query"),
    path("about/", views.about_page, name="about_page"),

]

urlpatterns += staticfiles_urlpatterns()