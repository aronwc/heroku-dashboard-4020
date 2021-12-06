#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gettingstarted.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from django.shortcuts import render
from django.http import HttpResponse
import requests
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap


homicides = ['Homicide Incidents', 'Homicide Arrests']
years = ['2019', '2020']

data = {
        'homicides' : homicides,
        '2019' : [124, 44],
        '2020' : [184, 49]
}

x = [(homicide, year) for homicide in homicides for year in years]
counts = sum(zip(data['2019'], data['2020']), ())

source = ColumnDataSource( data=dict(x=x, counts=counts))

plot = figure(x_range=FactorRange(*x), plot_height=250, title="Homicide: Incidents vs. Arrests", toolbar_location=None, tools="")

plot.vbar(x='x', top='counts', width=0.9, source=source, line_color = "white", fill_color=factor_cmap('x', palette=Spectral6, factors=years, start=1, end=2))

plot.y_range.start = 0
plot.x_range.range_padding = 0.1
plot.axis.major_label_orientation = 1
plot.xgrid.grid_line_color = None

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

curdoc().add_root(column(plot))
curdoc().add_root(column(plot2))