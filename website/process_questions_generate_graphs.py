from collections import Counter
from website.models import Response, Question, ResponseOptions, Survey 
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
import requests

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker
from bokeh.palettes import Spectral6, Category20c, Spectral3, Spectral8, Spectral10, Viridis, Viridis256
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.transform import factor_cmap, cumsum, jitter 
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.sampledata.commits import data as comdata
from bokeh.io import show, output_file
from bokeh.transform import factor_cmap
from bokeh.layouts import widgetbox
import math
import pandas as pd
import numpy as np
from django.db.models import Count

import itertools as it


class BarChart:
	''' 
	Given a query set of questions that have identical question_text (or possibly in the 
	same content set for future purposes), BarChart.generate() returns the HTML components 
	needed for the corresponding bar chart of the categorical data.
	'''

	@classmethod
	def generate(cls, question_query_set, **kwargs):
		all_responses = list()
		for q in question_query_set:
			all_responses += [r.choice_clean_text for r in q.response_set.all()]
			#q.response_set.all().values('choice_clean_text')
		counter = Counter(all_responses)
		print(counter)

		choices = list(counter.keys())
		counts = list(counter.values())

		df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
		df.rename(columns={'index': 'Choice Text', 0: 'Total'}, inplace=True)
	
		source = ColumnDataSource(data=dict(choices=choices, counts=counts, color=Viridis256[0:256:256 // len(choices)][:len(choices)]))

		p = figure(x_range=choices, y_range=(0,max(counts)*1.05), height=500, title=str(question_query_set[0].question_clean_text),
		           toolbar_location=None, tools="")

		p.vbar(x='choices', top='counts', width=0.9, color='color', source=source)

		p.xgrid.grid_line_color = None
		#p.legend.orientation = "horizontal"
		#p.legend.location = "top_center"
		p.xaxis.major_label_orientation = -math.pi/3

		return [components(p), df]

	def __str__(self):
		return "bar"

class TwoQuestionsStackedBar:
	@classmethod
	def generate(cls, question_query_set, question_query_set_2, **kwargs):
		df = pd.DataFrame(Response.objects.filter(question__in=question_query_set).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))
		df1 = pd.DataFrame(Response.objects.filter(question__in=question_query_set_2).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))
		print("\n" * 4)
		print(df)
		print("\n" * 4)
		print(df1)
		merged = df.merge(df1, how='outer', on='responder_id')
		both_merged = merged[(merged['question__question_clean_text_x'].apply(lambda x: isinstance(x, str))) & (merged['question__question_clean_text_y'].apply(lambda x: isinstance(x, str)))]
		counts_df = pd.crosstab(both_merged.choice_clean_text_x, both_merged.choice_clean_text_y)
		stackable_list = list(counts_df.columns)
		print("\n" * 4)
		print(counts_df)
		print("\n" * 4)
		counts_df.reset_index(level=['choice_clean_text_x'], inplace=True)
		data = dict()
		for c in counts_df.columns:
			data[c] = counts_df[c].tolist()
		p = figure(x_range=data['choice_clean_text_x'], y_range=(0, counts_df[stackable_list].sum(1).max() * 1.05), height=700,
					title="{} vs. {}".format(question_query_set[0].question_clean_text, question_query_set_2[0].question_clean_text),
					toolbar_location='right', tools="hover", tooltips="$name @{}: @$name".format('choice_clean_text_x'))
		p.vbar_stack(stackable_list, x='choice_clean_text_x', width=0.4,
					color=Viridis256[0:256:256 // len(stackable_list)][:len(stackable_list)], source=data, legend_label=stackable_list)
		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xgrid.grid_line_color = None
		p.axis.minor_tick_line_color = None
		p.outline_line_color = None
		p.legend.location = "top_right"
		p.legend.orientation = "vertical"
		p.xaxis.major_label_orientation = -math.pi/3
		counts_df.set_index('choice_clean_text_x', inplace=True)
		return [components(p), counts_df]
	def __str__(self):
		return "two questions stacked bar"


class StackedBarChart:

	@classmethod
	def generate(cls, question_query_set, stack_input, **kwargs):
		# show_fiture=False, return_html=True
		if stack_input == 'court':
			survey_attribute = 'survey__court_id'
		elif stack_input == 'year':
			survey_attribute = 'survey__survey_year'

		df = pd.DataFrame(Response.objects.filter(question__in=question_query_set).values(survey_attribute, 'choice_clean_text').annotate(count=Count('choice_clean_text')))
		#df = pd.DataFrame(Response.objects.filter(question__in=question_query_set).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))
		#df1 = pd.DataFrame(Response.objects.filter(question__in=question_query_set_2).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))

		#pivot = pd.pivot_table(df, values=['count'], index=['choice_clean_text'], columns=['survey__court_id'])
		pivot1 = pd.pivot_table(df, values=['count'], index=[survey_attribute], columns=['choice_clean_text'])

		pivot1.columns = [t[1] for t in list(pivot1.columns)]
		#pivot.columns = ['magistrate', 'municipal']
		stackable_list = list(pivot1.columns) # we want the columns from here before we reset_index
		print(stackable_list)

		#pivot.reset_index(level=['choice_clean_text'], inplace=True)
		#pivot.fillna(0, inplace=True)
		pivot1.reset_index(level=[survey_attribute], inplace=True)
		pivot1.fillna(0, inplace=True)
		print(pivot1.columns)

		data = dict()
		for c in pivot1.columns:
			data[c] = pivot1[c].tolist()
		data[survey_attribute] = list(map(str, data[survey_attribute])) # cast stack input to string, in case int
		surveys = data[survey_attribute]
		print(data)

		p = figure(x_range=surveys, y_range=(0, pivot1[stackable_list].sum(1).max() * 1.05), height=700, title="Responses by {}".format(stack_input),
					toolbar_location='right', tools="hover", tooltips="$name @{}: @$name".format(survey_attribute))

		p.vbar_stack(stackable_list, x=survey_attribute, width=0.4,
					color=Viridis256[0:256:256 // len(stackable_list)][:len(stackable_list)], source=data, legend_label=stackable_list)

		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xgrid.grid_line_color = None
		p.axis.minor_tick_line_color = None
		p.outline_line_color = None
		p.legend.location = "top_right"
		p.legend.orientation = "vertical"
		p.xaxis.major_label_orientation = -math.pi/3
		return [components(p), pivot1]

	def __str__(self):
		return "stacked bar"

class GroupedBarChart:

	@classmethod
	def generate_grouped(cls, question_query_set, group_input, **kwargs):
		if group_input == 'court':
			survey_attribute = 'survey__court_id'
		elif group_input == 'year':
			survey_attribute = 'survey__survey_year'

		df = pd.DataFrame(Response.objects.filter(question__in=question_query_set).values(survey_attribute, 'choice_clean_text').annotate(count=Count('choice_clean_text')))

		#pivot = pd.pivot_table(df, values=['count'], index=['choice_clean_text'], columns=['survey__court_id'])
		pivot1 = pd.pivot_table(df, values=['count'], index=[survey_attribute], columns=['choice_clean_text'])

		pivot1.columns = [t[1] for t in list(pivot1.columns)]
		#pivot.columns = ['magistrate', 'municipal']
		responses_list = list(pivot1.columns) # we want the columns from here before we reset_index

		#pivot.reset_index(level=['choice_clean_text'], inplace=True)
		#pivot.fillna(0, inplace=True)
		pivot1.reset_index(level=[survey_attribute], inplace=True)
		pivot1.fillna(0, inplace=True)

		data = dict()
		for c in pivot1.columns:
			data[c] = pivot1[c].tolist()
		data[survey_attribute] = list(map(str, data[survey_attribute])) # cast stack input to string, in case int
		surveys = data[survey_attribute]

		x = [ (year, response) for year in data[survey_attribute] for response in responses_list]
		counts = sum(zip(*[data[r] for r in responses_list]), ())

		source = ColumnDataSource(data=dict(x=x, counts=counts))

		p = figure(x_range=FactorRange(*x),  y_range=(0, pivot1[responses_list].sum(1).max() * 1.05), height=700, title="Responses by {}".format(group_input),
					toolbar_location=None, tools="")

		p.vbar(x='x', top='counts', width=0.9, source=source)

		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xaxis.major_label_orientation = 1
		p.xgrid.grid_line_color = None
		return [components(p), pivot1]

	def __str__(self):
		return "grouped bar"

class StackedGroupedBarChart:

	@classmethod
	def generate(cls, question_query_set, stack_input, group_input, **kwargs):
		stack_group_mappings = {'court': 'survey__court_id', 'year': 'survey__survey_year'}
		df = pd.DataFrame(Response.objects.filter(question__in=question_query_set).values(stack_group_mappings[stack_input], stack_group_mappings[group_input], 'choice_clean_text').annotate(count=Count('choice_clean_text')))
		pivot1 = pd.pivot_table(df, values=['count'], index=[stack_group_mappings[stack_input], stack_group_mappings[group_input]], columns=['choice_clean_text'])

		factors = list(pivot1.index)
		factors = [(str(t[0]), str(t[1])) for t in factors] # cast all elements of factors to strings
		pivot1.columns = pivot1.columns.get_level_values(1)
		pivot1.fillna(0, inplace=True)
		data = {'x': factors}
		for c in pivot1.columns:
			data[c] = pivot1[c].tolist()
		source = ColumnDataSource(data=data)
		p = figure(x_range=FactorRange(*factors), y_range=(0, pivot1.sum(1).max() * 1.05), 
			height=700)
		p.vbar_stack(list(map(str, pivot1.columns)), x='x', width=0.9, alpha=0.5, color=Viridis256[0:256:256 // len(pivot1.columns)][:len(pivot1.columns)], 
			source=source, legend_label=list(map(str, pivot1.columns)))

		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xaxis.major_label_orientation = 1
		p.xgrid.grid_line_color = None
		p.legend.location = "top_right"
		p.legend.orientation = "vertical"
		print(pivot1.index)
		return [components(p), pivot1]
	def __str__(self):
		return "stacked grouped bar"

class PieChart:
	@classmethod
	def generate(cls, question_query_set, **kwargs):
		all_responses = list()
		for q in question_query_set:
			all_responses += [r.choice_clean_text for r in q.response_set.all()]
			#q.response_set.all().values('choice_clean_text')
		counter = Counter(all_responses)
		print(counter)
		df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
		df.rename(columns={'index': 'Choice Text', 0: 'Total'}, inplace=True)

		data = pd.Series(counter).reset_index(name="value").rename(columns={'index': 'response'})
		data['angle'] = data['value']/data['value'].sum() * 2*math.pi
		data['color'] = Category20c[len(counter)]
		plot2 = figure(height=350, title=str(question_query_set[0].question_clean_text), 
		toolbar_location=None, tools="hover", tooltips="@possible_responses: @counts", x_range=(-0.5, 1.0))

		plot2.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='response', source=data)

		plot2.axis.axis_label = None
		plot2.axis.visible = False
		plot2.grid.grid_line_color = None

		script1, div1 = components(plot2)

		return [components(plot2), df]

	def __str__(self):
		return "pie"

class ScatterPlot(): #can be used for categorical variables with continuous values; eg time
	#ColumnDataSource takes in pandas dataframe....not sure which variable that is
	@classmethod
	def generate(cls, question_query_set, **kwargs):
		all_responses = list()
		for q in question_query_set:
			all_responses += [r.choice_clean_text for r in q.response_set.all()]
			#q.response_set.all().values('choice_clean_text')
		print(all_responses)
		counter = Counter(all_responses)
		print(counter)
		print("question_query_set: ", question_query_set)
		print("commit dataframe: ", comdata)

		choices = list(all_responses.keys())
		counts = list(all_responses.values())
		DAYS = ['Sun', 'Sat', 'Fri']
		# choices = [1, 2, 3, 4, 5]
		# counts = [7, 5, 3, 6, 4]
		source = ColumnDataSource(data=dict(choices=choices, counts=counts))
		# data = pd.Series(counter).reset_index(name="value").rename(columns={"index": "response"})
		plot = figure(x_range = counts, y_range=choices, height=300, title=str(question_query_set[0]),
		 toolbar_location=None, tools="hover", sizing_mode="stretch_width")

		plot.circle(x="choice", y=jitter("count", width=0.6, range=plot.y_range), source=comdata, alpha=0.3)

		# plot2 = figure(title=str(question_query_set[0]), tools="hover")
		# plot2.xaxis.axis_label = "x-axis"
		# plot2.yaxis.axis_label = "y-axis"
		# plot2.scatter(choices, counts)

		script1, div1 = components(plot)

		return components(plot)

	def __str__(self):
		return "scatter"

class HeatMap():
	@classmethod
	def generate(cls, question_query_set):
		return

	def __str__(self):
		return "heatmap"

class BoxPlot():
	@classmethod
	def generate(cls, question_query_set):
		return 

	def __str__(self):
		return "boxplot"

class LineGraph():
	@classmethod
	def generate(cls, question_query_set):
		return 

	def __str__(self):
		return "line"

class Table():
	@classmethod
	def generate(cls, question_query_set):
		#output_file("survey_dashboard.html")
		all_responses = list()
		for q in question_query_set:
			all_responses += [r.choice_clean_text for r in q.response_set.all()]

		counter = Counter(all_responses)
		print(counter)

		choices = list(counter.keys())
		counts = list(counter.values())

		print("choices: ", choices)
		print("counts: ", counts)

		print("choices: ", choices)
		print("counts: ", counts)
		# choices = [1, 2, 3, 4, 5]
		# counts = [7, 5, 3, 6, 4]
		source = ColumnDataSource(data=dict(choices=choices, counts=counts))

		columns = [
			TableColumn(field=choices, title="Choices"),
			TableColumn(field=counts, title="Counts"),
		]

		data_table = DataTable(source=source, columns=columns, width=400, height=280)

		#show(data_table)
		return components(data_table)

	def __str__(self):
		return "table"
		

def determine_valid_graph_types(question_type_subtype_tuple):
	''' Returns list of valid graph types given a tuple of form (question_type, question_subtype) '''
	question_type_subtype_graph_type_mapping = {
								('single_choice', 'vertical'): [BarChart(), PieChart(), TwoQuestionsStackedBar()],
								('open_ended', 'essay'): [],
								('open_ended', 'single'): [],
								('multiple_choice', 'vertical'): [BarChart(), PieChart(), TwoQuestionsStackedBar()],
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
