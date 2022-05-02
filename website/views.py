
from math import pi
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q, Count
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from .models import Response, Question, ResponseOptions, Survey, DocketCharge, DocketProceeding
from django.conf import settings
import requests
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker, HoverTool
from bokeh.palettes import Spectral6, Category20c
from bokeh.transform import factor_cmap, cumsum
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.io import show, output_file
from bokeh.layouts import widgetbox
from django.http import JsonResponse
import json
import pandas as pd
import numpy as np
import psycopg2
import io
import zipfile

from collections import Counter

from .process_questions_generate_graphs import *
from .question_id_mappings import *

chart_mappings = {'bar': BarChart(), 'stacked bar': StackedBarChart(), 'grouped bar': GroupedBarChart(), 'pie': PieChart(), 'table': Counter_Table()}


@login_required
def survey_dashboard(request):
    # this shouldnt be hard coded
    years = [x['survey_year'] for x in list(Survey.objects.order_by().values('survey_year').distinct())]
    context = {'courts': ['cdc', 'magistrate', 'municipal'], 'years': years}
    return render(request, 'website/survey_dashboard.html', context)


@login_required
def get_years_ajax(request):
    '''This function gets executed when Court drop down on display/ page clicked'''
    if request.method == "GET":
        try:
            surveys_with_courts_selected = Survey.objects.filter(court_id__in=json.loads(request.GET['courts']))
            # if any of the selected courts have an instance with year x, year x in this query set; else, not in
            # THESE ARE THE YEARS TO DISPLAY on drop down BASED ON selected courts
            years_to_display = surveys_with_courts_selected.order_by('survey_year').distinct()
            # these are the years that have been/are selected
            # this might need to be changed to survey start date

            surveys_with_years_selected = Survey.objects.filter(survey_year__in=json.loads(request.GET['years']))
            questions_to_display = Question.objects.filter(survey__in=surveys_with_years_selected & surveys_with_courts_selected)
            #questions_to_display = Question.objects.filter(survey_id__in=final_filtered_survey_ids).distinct()
            questions_to_display_final = questions_to_display.values('question_clean_text', 'cluster_id').annotate(num_responses=Count('response')).filter(num_responses__gt=0).distinct()
        except Exception as e:
            print(e)
            print("ERROR")
            return HttpResponse('yo')
        return JsonResponse(list(years_to_display.values('survey_year')) + list(questions_to_display_final.values('question_clean_text')), safe=False)

@login_required
def get_questions_ajax(request):
    '''This function gets executed when Year drop down on display/ page clicked'''
    if request.method == "GET":
    
        try:
            surveys_with_courts_selected = Survey.objects.filter(court_id__in=json.loads(request.GET['courts']))
            # these are the years that have been/are selected
            # this might need to be changed to survey start date
            surveys_with_years_selected = Survey.objects.filter(survey_year__in=json.loads(request.GET['years']))
            questions_to_display = Question.objects.filter(survey__in=surveys_with_years_selected & surveys_with_courts_selected)
            # we only want to display questions that are in a 'content set' that has responses
            questions_to_display_final = questions_to_display.values('question_clean_text', 'cluster_id').annotate(num_responses=Count('response')).filter(num_responses__gt=0).distinct()
        except Exception as e:

            return HttpResponse('yo')
        print("questions: ", questions_to_display_final)
        return JsonResponse(list(questions_to_display_final.values('question_clean_text')), safe=False)

def get_graphs_ajax(q_type, q_subtype):

    allowable_graph_types = determine_valid_graph_types((q_type, q_subtype))
    data = [{"graph_type":str(v)} for v in allowable_graph_types]
    print("data is: ", data)
    return data

def get_question_type_subtype(question_query_set):
    df = pd.DataFrame(question_query_set.values('question_type', 'question_subtype').annotate(count=Count('question_id')))
    q_type, q_subtype = df.iloc[df['count'].idxmax()]['question_type'], df.iloc[df['count'].idxmax()]['question_subtype']
    return q_type, q_subtype

def get_raw_data(*args):
    ''' Given QuerySets, returns a list of DataFrames, one for each QuerySet (aka equivalent to the raw data) '''
    csvs_dict= dict()
    for qs in args:
        #csvs_dict
        dfs_list.append(pd.DataFrame.from_records(qs.values()))
    return dfs_list

@login_required
def generate_panel_2_options(request):
    if request.method == "GET":
        surveys_with_courts_selected = Survey.objects.filter(court_id__in=json.loads(request.GET['courts']))
        surveys_with_years_selected = Survey.objects.filter(survey_year__in=json.loads(request.GET['years']))
        question_1_selected_first_instance_cluster_id = Question.objects.filter(question_clean_text=json.loads(request.GET['question_1']))[0].cluster_id
        qs1 = Question.objects.filter(Q(cluster_id=question_1_selected_first_instance_cluster_id) | Q(question_clean_text=json.loads(request.GET['question_1']))) # query set of all questions with matching cluster id OR clean text
        global qs2
        qs2 = Question.objects.filter(survey__in=surveys_with_years_selected & surveys_with_courts_selected) # query set of all questions meeting court and year filters
        '''
        we can define these variables as global here so that we only execute the code to get them once
        any time Question 1 drop down is clicked, this function is called, so these variables will always reflect that selection
        which is what we want!
        '''

        global all_similar_questions_query_set, q_type, q_subtype
        # get all questions that are meaning-identical
        all_similar_questions_query_set = (qs1 & qs2)
        q_type, q_subtype = get_question_type_subtype(all_similar_questions_query_set)

        data = {'question_type': q_type, 'question_subtype': q_subtype}
        data['questions'] = []
        data['sub_questions'] = list()
        # for vertical subtype questions, we can pick a second vertical subtype question to compare by
        # so we want to filter Question 2 dropdown to show only those
        if q_subtype == "vertical":
            qs3 = Question.objects.filter(question_subtype="vertical")
            questions_2_to_display = (qs2 & qs3)
            questions_2_to_display_final = questions_2_to_display.values('question_clean_text', 'cluster_id').annotate(num_responses=Count('response')).filter(num_responses__gt=0).distinct()
            data['questions'] = list(questions_2_to_display_final.values('question_clean_text'))
        elif q_type == 'matrix' and q_subtype == 'single':
            sub_questions = ResponseOptions.objects.filter(question__in=all_similar_questions_query_set)
            data['sub_questions'] = list(sub_questions.values('row_text').distinct())
        
        data['graphs'] = get_graphs_ajax(q_type, q_subtype)

        return JsonResponse(data, safe=False)

    
@login_required
def process_generate(request):
    if request.method == "GET":
        selected_sub_questions_text = json.loads(request.GET['sub_questions'])
        graph_type = str(json.loads(request.GET['chart_type'])[0])
        all_similar_questions_query_set_2 = ''
        if q_subtype == 'vertical':
            # get the id of the first question in the database with an exact text match to the selected one
            question_2_selected_first_instance_cluster_id = Question.objects.filter(question_clean_text=json.loads(request.GET['question_2']))[0].cluster_id
            qs3 = Question.objects.filter(Q(cluster_id=question_2_selected_first_instance_cluster_id) | Q(question_clean_text=json.loads(request.GET['question_2']))) # query set of all questions with matching cluster id OR clean text
            # get all questions that are meaning-identical
            all_similar_questions_query_set_2 = (qs3 & qs2)
            print(json.loads(request.GET['question_2']))
            print("len all_similar_questions_query_set_2: {}".format(len(all_similar_questions_query_set_2)))
            returned = chart_mappings[graph_type].generate(all_similar_questions_query_set, query_set_2=all_similar_questions_query_set_2, qs_type='question')
            script, div = returned[0]
            table_html = returned[1].to_html()
            return JsonResponse({'script': [script], 'div': [div], 'table_html': [table_html]})
        elif q_type == 'matrix' and q_subtype == 'single':
            # list of QuerySets, one for all ResponseOptions rows for selected graphs
            script_divs = list()
            tables = list()
            # WE ARE MATCHING ON TEXT HERE BUT WE WANT TO MATCH ON MEANING (NLP) LIKE SARAH DID WITH QUESTIONS!!!!!!!!
            for sqt in selected_sub_questions_text:
                sq_query_set = ResponseOptions.objects.filter(row_text=sqt)
                returned = chart_mappings[graph_type].generate(sq_query_set, qs_type='response_option')
                script_divs.append(returned[0])
                tables.append(returned[1].to_html())

            return JsonResponse({'script': [t[0] for t in script_divs], 'div': [t[1] for t in script_divs], 'table_html': tables, 
                                'question_type': q_type, 'question_subtype': q_subtype})

            

@login_required
def stack_group_bar_chart(request):
    if request.method == "GET":
        
        stack_input = json.loads(request.GET['stack_input'])
        group_input = json.loads(request.GET['group_input'])
        if stack_input != 'none' and group_input == 'none':
            chart_class = StackedBarChart()
        elif stack_input == 'none' and group_input != 'none':
            chart_class = GroupedBarChart()
        else:
            chart_class = StackedGroupedBarChart()

        script_divs = list()
        tables = list()

        if q_subtype == 'vertical':
            returned = chart_class.generate(all_similar_questions_query_set, qs_type='question', stack_input=stack_input, group_input=group_input)
            script, div = returned[0]
            table_html = returned[1].to_html()
            return JsonResponse({'script': [script], 'div': [div], 'table_html': [table_html]})
        elif q_type == 'matrix' and q_subtype == 'single':
            script_divs = list()
            tables = list()
            selected_sub_questions_text = json.loads(request.GET['sub_questions'])
            for sqt in selected_sub_questions_text:
                sq_query_set = ResponseOptions.objects.filter(row_text=sqt)
                returned = chart_class.generate(sq_query_set, qs_type='response_option', stack_input=stack_input, group_input=group_input)
                script_divs.append(returned[0])
                tables.append(returned[1].to_html())
            return JsonResponse({'script': [t[0] for t in script_divs], 'div': [t[1] for t in script_divs], 'table_html': tables})

@login_required
def dockets_dashboard(request):
    ''' 'Pass in context of all DocketCharges, filtered by -mag_num '''
    context = dict()
    return render(request, 'website/dockets_dashboard.html', context)

@login_required
def get_docket_charge_by_mag_num(request):
    pass

class SearchResultsList(ListView):
    ''' multiple inputs <input> given as comma separated values '''
    model = DocketCharge
    context_object_name = "docketcharges"
    template_name = "website/dockets_dashboard.html"
    def get_queryset(self):
        print('request:{}a'.format(self.request.GET.get("mag_num")))
        mag_num = int(self.request.GET.get("mag_num"))

        print(mag_num)
        mag_num_query = Q(mag_num=mag_num)
        return DocketCharge.objects.filter(mag_num_query)
        
        Q_objects = list()
        if judge != '':
            Q_objects.append(Q(judge__in=judges))
        if charges != '':
            Q_objects.append(Q(charge__in=charges))
        if time_range != '':
            Q_objects.append(Q(date__range=(start_date, end_date))) # inclusive
        if bond__range != '':
            Q_objects.append(Q(bond__range=(min_bond, max_bond)))


        return DocketCharge.objects.filter(*Q_objects)


class LoginView(LoginView):
    template_name = 'error_login.html'
    print("this is the loginview")
    def my_view(request):
        print("this is myview")
        if not request.user.is_authenticated:
            return render(request, 'website/error_login.html')


def logout_view(request):
    logout(request)
    
@login_required
def about_page(request):
    return render(request, 'website/about_page.html')
