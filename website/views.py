
from math import pi
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Response, Question, ResponseOptions, Survey, DocketCharge, DocketProceeding
import requests
from website.models import Response, Question, ResponseOptions, Survey 
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap
#from .models import Response, Question, ResponseOptions, Survey, DocketCharge, DocketProceeding
import requests
from website.models import Response_new, Question, ResponseOptions, Survey 
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6, Category20c
from bokeh.transform import factor_cmap, cumsum

from django.http import JsonResponse
import json
import pandas as pd
import numpy as np
import psycopg2


def index(request):
    return HttpResponse('yo')


# Create your views here.
def test(request):
    #return HttpResponse('Hello from Python!')
    return render(request, "test.html")

def plot(request):

    courts = ["Criminal District", "Magistrate", "Municipal"]
    years = ["2016", "2017", "2018", "2019", "2020"]

    data = {
        'courts' : courts,
        '2016' : [300, 200, 100], #made up
        '2017' : [331, 278, 170],
        '2018' : [409, 255, 146],
        '2019' : [482, 334, 171],
        '2020' : [295, 278, 143],
    }
    
    a = [(court, year) for court in courts for year in years]
    #count = sum(zip(data['2016'], data['2017'], data['2016'], data['2016'], data['2020']))


    #Homicide Incidents and Arrests Bar Graph
    homicides = ['Homicide Incidents', 'Homicide Arrests']
    years = ['2019', '2020']
    data = {
        'homicides' : homicides,
        '2019' : [124, 44],
        '2020' : [184, 49]
    }
    x = [(homicide, year) for homicide in homicides for year in years]
    counts = sum(zip(data['2019'], data['2020']), ())
    source = ColumnDataSource(data=dict(x=x, counts=counts))
    plot = figure(x_range=FactorRange(*x), plot_height=250, title="Homicide: Incidents vs. Arrests", toolbar_location=None, tools="")
    plot.vbar(x='x', top='counts', width=0.9, source=source, line_color = "white", fill_color=factor_cmap('x', palette=Spectral6, factors=years, start=1, end=2))
    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.axis.major_label_orientation = 1
    plot.xgrid.grid_line_color = None

    #Line Graph
    i = ["2019", "2020"]
    j = [2632, 2105]
    plot2 = figure(title = "Number of Domestic Violence Arrests", x_axis_label = "X-axis", y_axis_label = "Y-axis",plot_width = 400, plot_height = 400, x_axis_type="datetime", toolbar_location=None)
    plot2.line(i, j, line_width = 2)
    plot2.xaxis.bounds = (2018, 2021)
    plot2.xaxis.ticker = FixedTicker(ticks=[2019, 2020])
    plot2.xaxis.axis_label = "Year"
    plot2.yaxis.axis_label = "Arrests(person-arrest events)"
    plot2.y_range = Range1d(0, 3000)
    plot2.toolbar.active_drag = None
    plot2.toolbar.active_scroll = None
    plot2.toolbar.active_tap = None

    script1, div1 = components(plot)
    script2, div2 = components(plot2)

    return render(request, 'pages/base.html', {'script1':script1, 'div1':div1, 'script2':script2, 'div2':div2})

# do pie chart here with bokeh
def pretrial(request):
    print('made')
    good_qs_list = Question.objects.filter(question_text__contains='What is the defendant\x92s pretrial risk score?')

    good_qs_ids = [q.question_id for q in list(good_qs_list)]

    good_responses_list = list(Response.objects.filter(question_id__in=good_qs_ids))


    output = ', '.join([r.response_text for r in good_responses_list])

    return HttpResponse(output)

# pie chart with bokeh
def afford_bond(request):
    pass

def display(request):
    # this shouldnt be hard coded
    context = {'courts': ['cdc', 'magistrate', 'municipal']}
    return render(request, 'website/display.html', context)

def get_topics_ajax(request):
    if request.method == "GET":
    
        try:

            # get a QuerySet returning all entries of Survey table that have court.id = to selected court
            court = Survey.objects.filter(court_id=json.loads(request.GET['court_id']))


            survey_ids_list = [s.survey_id for s in list(court)]

            questions = Question.objects.filter(survey_id__in=survey_ids_list)
            #print(list(questions.values('question_text')))

        except Exception:
            #data['error_message'] = 'error'
            return HttpResponse(yo)
        return JsonResponse(list(questions.values('question_text')), safe=False)

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
    return render(request, 'pages/responses_test.html')

# do pie chart here with bokeh
def pretrial(request):
    good_qs_list = Question.objects.filter(question_text__contains='What is the defendant\x92s pretrial risk score?')
    #print("list is ", good_qs_list)
    good_qs_ids = [q.question_id for q in list(good_qs_list)]
    #print("id is ", good_qs_ids)
    good_responses_list = list(Response_new.objects.filter(question_id__in=good_qs_ids))
    output = ', '.join([r.response_text for r in good_responses_list])
    possible_responses = [ '0', '1', '2', '3', '4', '5' ]

    counts = [ output.count('0'), output.count('1'), output.count('2'), output.count('3'), output.count('4'), output.count('5')] #ignore 99
    source = ColumnDataSource(dict(possible_responses=possible_responses, counts=counts))
    
    #Bar Graph
    plot = figure(x_range=FactorRange(*possible_responses), plot_height=250, title="What is the defendant's pretrial risk score?", toolbar_location=None, tools="", x_axis_label = "Score", y_axis_label = "Total Count")
    plot.vbar(x='possible_responses', top='counts', width=0.9, source=source)

    plot.xgrid.grid_line_color = None
    plot.y_range.start = 0

    script,div = components(plot)

    
    #Pie Chart
    x = {
        '0':output.count('0'),
        '1':output.count('1'),
        '2':output.count('2'),
        '3':output.count('3'),
        '4':output.count('4'),
        '5':output.count('5'),
    }
    print(x)
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

    script1, div1 = components(plot2)

    return render(request, 'pages/pretrial.html', {'script':script, 'div':div, 'script1':script1, 'div1': div1}) 


# pie chart with bokeh
def afford_bond(request):
    pass
