from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Response, Question, ResponseOptions, Survey
import requests
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap
from django.http import JsonResponse
import json

# Create your views here.
def index(request):
    #return HttpResponse('Hello from Python!')
    return render(request, "index.html")
    #r = requests.get('http://httpbin.org/status/418')
    #print(r.text)
    #return HttpResponse('<pre>' + r.text + '</pre>')

def plot(request):
    #Number of Case Appearances Observed Bar Graph
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
    print(request)
    if request.method == "GET":
        print('made0')
        #court_id = request.POST['court_id']
        #court 
        print('court_id is {}'.format(request.GET['court_id']))
        #data = json.loads(request.body)
        #print(data)
        try:
            print('made1')
            # get a QuerySet returning all entries of Survey table that have court.id = to selected court
            court = Survey.objects.filter(court_id=json.loads(request.GET['court_id']))
            print('made2')
            survey_ids_list = [s.survey_id for s in list(court)]
            print('made3')
            questions = Question.objects.filter(survey_id__in=survey_ids_list)
            print('made4')
            print('questions[0].text is {}'.format(questions[0].question_text[:50]))
            print('question.values list is {}'.format(list(questions.values('question_text'))[:10]))
            print('\n'*3)
            print('json response is {}'.format(str(JsonResponse(list(questions.values('question_text')), safe=False))))
        except Exception:
            #data['error_message'] = 'error'
            print('made5')
            return HttpResponse(yo)
        return JsonResponse(list(questions.values('question_text')), safe=False)
        print('made-1')









