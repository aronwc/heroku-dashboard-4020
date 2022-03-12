from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from website.models import Responses
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap
import pandas as pd
import numpy as np
import psycopg2

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

    return render(request, 'pages/responses_test.html', {'script':script, 'div':div})