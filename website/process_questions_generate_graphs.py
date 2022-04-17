from collections import Counter
from website.models import Response, Question, ResponseOptions, Survey 
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
import requests

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6, Category20c, Spectral3, Spectral8, Spectral10, Viridis, Category20c

from bokeh.transform import factor_cmap, cumsum
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.sampledata.autompg import autompg_clean as df

from bokeh.transform import factor_cmap
import math
import pandas as pd
import numpy as np
from django.db.models import Count


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

		p = figure(x_range=choices, y_range=(0,max(counts)*1.05), height=500, title=str(question_query_set[0]),
		           toolbar_location=None, tools="")

		p.vbar(x='choices', top='counts', width=0.9, color='color', source=source)

		p.xgrid.grid_line_color = None
		#p.legend.orientation = "horizontal"
		#p.legend.location = "top_center"
		p.xaxis.major_label_orientation = -math.pi/3

		return components(p)

	@classmethod
	def generate_stacked(cls, question_query_set, stack_input):
		# show_fiture=False, return_html=True
		if stack_input == 'court':
			survey_attribute = 'survey__court_id'
		elif stack_input == 'year':
			survey_attribute = 'survey__survey_year'

		df = pd.DataFrame(Response.objects.filter(question__in=question_query_set).values(survey_attribute, 'choice_text').annotate(count=Count('choice_text')))

		print(df)
		print()
		print()
		#pivot = pd.pivot_table(df, values=['count'], index=['choice_text'], columns=['survey__court_id'])
		pivot1 = pd.pivot_table(df, values=['count'], index=[survey_attribute], columns=['choice_text'])
		print(pivot1)
		print()
		print(pivot1.index)
		print(list(pivot1.columns))
		pivot1.columns = [t[1] for t in list(pivot1.columns)]
		#pivot.columns = ['magistrate', 'municipal']
		stackable_list = list(pivot1.columns) # we want the columns from here before we reset_index
		print()
		print(pivot1)
		print()
		#pivot.reset_index(level=['choice_text'], inplace=True)
		#pivot.fillna(0, inplace=True)
		pivot1.reset_index(level=[survey_attribute], inplace=True)
		pivot1.fillna(0, inplace=True)
		print()
		print(pivot1)
		print()
		print(pivot1[stackable_list].sum(1).max())

		data = dict()
		for c in pivot1.columns:
			data[c] = pivot1[c].tolist()
		data[survey_attribute] = list(map(str, data[survey_attribute])) # cast stack input to string, in case int
		surveys = data[survey_attribute]
		print(data)

		p = figure(x_range=surveys, y_range=(0, pivot1[stackable_list].sum(1).max() * 1.05), height=700, title="Responses by {}".format(stack_input),
					toolbar_location='right', tools="hover", tooltips="$name @{}: @$name".format(survey_attribute))

		p.vbar_stack(stackable_list, x=survey_attribute, width=0.4,
					color=Spectral10[:len(stackable_list)], source=data, legend_label=stackable_list)

		'''
		data = dict()
		for c in pivot.columns:
			data[c] = pivot[c].tolist()
		choices = data['choice_text']

		p = figure(x_range=choices, y_range=(0,300), height=500, title="Responses by court",
					toolbar_location='right', tools="hover", tooltips="$name @choice_text: @$name")

		p.vbar_stack(['magistrate', 'municipal'], x='choice_text', width=0.9,
					color=["#c9d9d3", "#718dbf"], source=data, legend_label=['magistrate', 'municipal'])
		'''
		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xgrid.grid_line_color = None
		p.axis.minor_tick_line_color = None
		p.outline_line_color = None
		p.legend.location = "top_right"
		p.legend.orientation = "vertical"
		p.xaxis.major_label_orientation = -math.pi/3
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
		print(counter)

		data = pd.Series(counter).reset_index(name="value").rename(columns={'index': 'response'})
		data['angle'] = data['value']/data['value'].sum() * 2*math.pi
		data['color'] = Category20c[len(counter)]
		plot2 = figure(height=350, title=str(question_query_set[0]), 
		toolbar_location=None, tools="hover", tooltips="@possible_responses: @counts", x_range=(-0.5, 1.0))

		plot2.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='response', source=data)

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
