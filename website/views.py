from django.shortcuts import render
from django.http import HttpResponse
import requests
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components

#from .models import Greeting

# Create your views here.
#def index(request):
    # return HttpResponse('Hello from Python!')
    #return render(request, "index.html")
#    r = requests.get('http://httpbin.org/status/418')
#    print(r.text)
#    return HttpResponse('<pre>' + r.text + '</pre>')


#def db(request):
#
#    greeting = Greeting()
#    greeting.save()
#
#    greetings = Greeting.objects.all()
#
#    return render(request, "db.html", {"greetings": greetings})

def homepage(request):
    x = [1, 2, 3, 4, 5]
    y = [1, 2, 3, 4, 5]

    plot = figure(title = 'Line Graph', x_axis_label = 'X-axis', y_axis_label = 'Y-axis', plot_width = 400, plot_height = 400)
    plot.line(x, y, line_width = 2)
    script, div = components(plot)
    return render(request, 'pages/base.html', {'script' : script, 'div' : div } )
