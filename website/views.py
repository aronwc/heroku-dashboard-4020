
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
def bennett_bokeh(request):
    if request.method == "GET":
        print("IN BENNETT BOKEH")
     
       #create a plot
        plot = figure(plot_width=400, plot_height=400)
     
       # add a circle renderer with a size, color, and alpha
     
        plot.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)
     
        script, div = components(plot)
     
        #return render(request, 'website/bennett_bokeh.html', {'script': script, 'div': div})
        return JsonResponse({'script': script, 'div': div})

@login_required
# do pie chart here with bokeh
def pretrial(request):
    print('made')
    good_qs_list = Question.objects.filter(question_clean_text__contains='What is the defendant\x92s pretrial risk score?')

    good_qs_ids = [q.question_id for q in list(good_qs_list)]

    good_responses_list = list(Response.objects.filter(question_id__in=good_qs_ids))


    output = ', '.join([r.response_text for r in good_responses_list])

    return HttpResponse(output)

@login_required
# pie chart with bokeh
def afford_bond(request):
    pass

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


@login_required
def psql(request):
    
    #Number of Case Appearances Observed Bar Graph
    # for p in Responses.objects.raw('SELECT * FROM website_responses'):
    #    print(p)
    # def connect():
    #     print("Connecting to database...")
    #     conn = psycopg2.connect(
    #         host="localhost",
    #         database="website",
    #         user="django",
    #         password="Tulane4010"
    #         )
    #     df = pd.read_sql_query("""
    #             SELECT * FROM website_responses
    #             """, conn)
        
    #     #print(df)
    #     return df #put this in config instead; doesn't need to be in views
    # get_object_or_404() function
    # get a online version up with a single query using database
    #clean csv --> ucf-8
    # responses = connect()
    # data = dict(
    #      year = [d for d in responses['year']],
    #      id = [d for d in responses['id']],
    #     # court = [d['court'] for d in responses],
    #     # bail = [d['bail'] for d in responses],
    #     # judge = [d['judge'] for d in responses],
    #     # ethnicity = [d['ethnicity'] for d in responses],
    # )
    # #edit csv to count number of each element instead
    # source = ColumnDataSource(data)
    # print(data['year'])
    # count = data['year'].count(2020)
    
    # sorted_ids = sorted(source.year, key=lambda x: source.id[source.year.index(x)])

    homicides = ['Homicide Incidents', 'Homicide Arrests']
    yrs = ['2020', '2021']
    #years = ['2019', '2020']
    courts = ['Magistrate', 'Municipal', 'Criminal']
    # data = {
    #     'homicides' : homicides,
    #     '2019' : [124, 44],
    #     '2020' : [184, 49]
    # }
    data = {
        'yrs' : yrs,
        'Magistrate': [10, 20],
        'Municipal': [20, 10],
        'Criminal' : [15, 15]
    }
    #x = [(homicide, year) for homicide in homicides for year in years]
    x = [(yr, court) for yr in yrs for court in courts]
    #counts = sum(zip(data['2019'], data['2020']), ())
    counts = sum(zip(data['Magistrate'], data['Municipal'], data['Criminal']), ())
    source = ColumnDataSource(data=dict(x=x, counts=counts))
    plot = figure(x_range=FactorRange(*x), plot_height=250, title="Cases per Year", toolbar_location=None, tools="")
    plot.vbar(x='x', top='counts', width=0.9, source=source, line_color = "white", fill_color=factor_cmap('x', palette=Spectral6, factors=yrs, start=1, end=2))
    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.axis.major_label_orientation = 1
    plot.xgrid.grid_line_color = None
    
    script,div = components(plot)

    #return render(request, 'pages/responses_test.html', {'script':script, 'div':div})
    return render(request, 'website/responses_test.html')

@login_required
def pretrial(request):
    good_qs_list = Question.objects.filter(question_clean_text__contains='What is the defendant\x92s pretrial risk score?')
    #print("list is ", good_qs_list)
    good_qs_ids = [q.question_id for q in list(good_qs_list)]
    #print("id is ", good_qs_ids)
    good_responses_list = list(Response.objects.filter(question_id__in=good_qs_ids))
    output = ', '.join([r.response_text for r in good_responses_list])
    possible_responses = [ '0', '1', '2', '3', '4', '5' ]

    #counts = [ output.count('0'), output.count('1'), output.count('2'), output.count('3'), output.count('4'), output.count('5')] #ignore 99
    counts = [100, 122, 413, 52, 54, 610]
    source = ColumnDataSource(dict(possible_responses=possible_responses, counts=counts))
    
    #Bar Graph
    plot = figure(x_range=FactorRange(*possible_responses), plot_height=250, title="What is the defendant's pretrial risk score?", toolbar_location=None, tools="", x_axis_label = "Score", y_axis_label = "Total Count")
    plot.vbar(x='possible_responses', top='counts', width=0.9, source=source)

    plot.xgrid.grid_line_color = None
    plot.y_range.start = 0
    print("plot: ", plot)
    script,div = components(plot)
    #print("bar components: ", components(plot))
    
    # Pie Chart
    x = {
        '0':345,
        '1':31,
        '2':657,
        '3':864,
        '4':56,
        '5':200,
    }
    new_source = pd.Series(x).reset_index(name='counts').rename(columns={'index':'possible_responses'})
    new_source['angle'] = new_source['counts']/new_source['counts'].sum() *2*pi
    new_source['color'] = Category20c[len(x)]

    plot2 = figure(height=350, title="What is the defendant's pretrial risk score?", 
    toolbar_location=None, tools="hover", tooltips="@possible_responses: @counts", x_range=(-0.5, 1.0))

    plot2.wedge(x=0, y=1, radius=0.4,
    start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'), 
    line_color="white", fill_color="color", legend_field="possible_responses", source=new_source)

    plot2.axis.axis_label = None
    plot2.axis.visible = False
    plot2.grid.grid_line_color = None

    #script1, div1 = components(plot2)

	# for q in question_query_set:
	# 	all_responses += [r.choice_clean_text for r in q.response_set.all()]

	# counter = Counter(all_responses)
	# print(counter)
    source = ColumnDataSource(data=dict(possible_responses=["yes", "no", "maybe", "possibly", "terrible", "zzz"], counts=[100, 122, 413, 52, 54, 610]))
    columns = [
		TableColumn(field="possible_responses", title="possible responses"),
		TableColumn(field="counts", title="Counts"),
	]
    data_table = DataTable(source=source, columns=columns)

	# df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
	# df.rename(columns={'index': 'Choice Text', 0: 'Total'}, inplace=True)
    show(data_table)
    #script1, div1 = data_table
    print("data table components: ", data_table)
		#show(data_table)
	#return [components(data_table), df]
    script1, div1 = components(data_table)

    return render(request, 'website/pretrial.html', {'script':script, 'div':div, 'script1':script1, 'div1': div1}) 

@login_required
# pie chart with bokeh
def afford_bond(request):
    pass

class LoginView(LoginView):
    template_name = 'error_login.html'
    print("this is the loginview")
    def my_view(request):
        print("this is myview")
        if not request.user.is_authenticated:
            return render(request, 'website/error_login.html')
    # login_url = '/admin'
    # redirect_field_name = 'redirect_to'

# def my_view(request):
#     print("this is myview")
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         # Redirect to a success page.
#         ...
#     if not request.user.is_authenticated:
#         return render(request, 'myapp/login_error.html')

# def my_view(request):
#         print("this is myview")
#         if not request.user.is_authenticated:
#             return render(request, 'myapp/error_login.html')

def logout_view(request):
    logout(request)
    
@login_required
def about_page(request):
    return render(request, 'website/about_page.html')
