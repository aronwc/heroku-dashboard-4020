from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from website.models import Responses
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap

# Create your views here.
def test(request):
    #return HttpResponse('Hello from Python!')
    return render(request, "test.html")

def plot(request):
    #Number of Case Appearances Observed Bar Graph
    #for p in Responses.objects.raw('SELECT * FROM website_responses'):
    #    print(p)

    #TODO: Query responses to create visualizations

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
    # template = "pages/responses_test.html"
    # data = responses.objects.all()

    # prompt = {
    #     'order': 'Order of the CSV should be id, court, bail, judge, ethnicity',
    #     'rsps': data
    # }
    # if request.method == "GET":
    #     return render(request, template, prompt)
    
    # csv_file = request.FILES['file']

    # if not csv_file.name.endswith('.csv'):
    #     messages.error(request, "THIS IS NOT A CSV FILE")

    # data_set = csv_file.read().decode("UTF-8")

    # io_string = io.StringIO(data_set)
    # next(io_string)
    # for column in csv.reader(io_string, delimiter=",", quotechar="|"):
    #     _, created = responses.objects.update_or_create(
    #         id=column[0],
    #         court=column[1],
    #         bail=column[2],
    #         judge=column[3],
    #         ethnicity=column[4],
    #     )
    # context = {}

    #return render(request, template, context)
    return