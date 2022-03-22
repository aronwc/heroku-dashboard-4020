from collections import Counter
from website.models import Response, Question, ResponseOptions, Survey 
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
import requests
from bokeh.palettes import Spectral6, Category20c, Magma, Inferno, Plasma, Viridis
from bokeh.transform import factor_cmap, cumsum
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.sampledata.autompg import autompg_clean as df
from math import pi
import pandas as pd

class BarChart:
	''' 
	Given a query set of questions that have identical question_text (or possibly in the 
	same content set for future purposes), BarChart.generate() returns the HTML components 
	needed for the corresponding bar chart of the categorical data.
	'''

	@classmethod
	def generate(cls, question_query_set):
		all_responses = list()
		print('question_query_set in BarChart.generate: {}'.format(question_query_set))
		print()
		print([q.question_id for q in question_query_set])
		for q in question_query_set:
			all_responses += [r.choice_text for r in q.response_set.all()]
			#q.response_set.all().values('choice_text')
		counter = Counter(all_responses)
		print(counter)

		choices = list(counter.keys())
		counts = list(counter.values())

		source = ColumnDataSource(data=dict(choices=choices, counts=counts, color=Spectral6))

		p = figure(x_range=choices, y_range=(0,9), height=250, title=str(question_query_set[0]),
		           toolbar_location=None, tools="")

		p.vbar(x='choices', top='counts', width=0.9, color='color', legend_field="choices", source=source)

		p.xgrid.grid_line_color = None
		p.legend.orientation = "horizontal"
		p.legend.location = "top_center"

		return components(p)


	def __str__(self):
		return "bar"

class PieChart:
	@classmethod
	def generate(cls, question_query_set):
		all_responses = list()
		for q in question_query_set:
			all_responses += [r.choice_text for r in q.response_set.all()]
			#q.response_set.all().values('choice_text')
		counter = Counter(all_responses)
		#print(counter)

		choices = list(counter.keys())
		counts = list(counter.values())
		choices_len = len(choices)
		
		plot2 = figure(height=350, title="What is the defendant's pretrial risk score?", 
		toolbar_location=None, tools="hover", tooltips="@possible_responses: @counts", x_range=(-0.5, 1.0))

		plot2.wedge(x=0, y=1, radius=0.4,
		start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'), 
		line_color="white", fill_color=Viridis[len(choices)], legend_field="possible_responses")

		plot2.axis.axis_label = None
		plot2.axis.visible = False
		plot2.grid.grid_line_color = None

		script1, div1 = components(plot2)

		return components(plot2)

	def __str__(self):
		return "pie"


def determine_valid_graph_types(question_type_subtype_tuple):
	''' Returns list of valid graph types given a tuple of form (question_type, question_subtype) '''
	question_type_subtype_graph_type_mapping = {
								('single_choice', 'vertical'): [BarChart(), PieChart()],
								('open_ended', 'essay'): [],
								('open_ended', 'single'): [],
								('multiple_choice', 'vertical'): [],
								('open_ended', 'numerical'): [],
								('single_choice', 'vertical_two_col'): [],
								('open_ended', 'multi'): [],
								('matrix', 'single'): [],
								('matrix', 'rating'): [],
								('datetime', 'time_only'): [],
								('single_choice', 'menu'): [],
								('datetime', 'date_only'): []
	}

	return question_type_subtype_graph_type_mapping[question_type_subtype_tuple]





