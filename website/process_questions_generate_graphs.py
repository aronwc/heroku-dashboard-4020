from collections import Counter
from website.models import Response, Question, ResponseOptions, Survey 
from bokeh.plotting import figure, output_file, show
import requests
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Range1d, DatetimeTickFormatter, FixedTicker, HoverTool
from bokeh.palettes import Spectral6, Category20c, Spectral3, Spectral8, Spectral10, Viridis, Viridis256
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.transform import factor_cmap, cumsum, jitter 
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

stack_group_mappings = {'court': 'survey__court_id', 'year': 'survey__survey_year'}


class BarChart:
	"""
	Given a query set of questions that have identical question_text (or possibly in the 
	same cluster set for future purposes), BarChart.generate() returns the HTML components 
	needed for the corresponding bar chart of the categorical data.

	Methods
	-------
	generate(cls, query_set, *args, **kwargs)

	"""

	@classmethod
	def generate(cls, query_set, *args, **kwargs):
		"""
		- Method called to to generate a bar chart
		- Returns the HTML script/div combo required for Bokeh visualizations

		Parameters
		----------
		* query_set (Django QuerySet): QuerySet of Question(s) or ResponseOption(s) to graph

		Returns
		-------
		[components(p), df]
			* components(p) (tuple) -> (script, div), where:
				- script is HTML of script for Bokeh chart
				- div is HTML of div for Bokeh chart
			* df (pd.DataFrame) -> the 'raw' data of the table
		"""
		qs_type = kwargs['qs_type']
		all_responses = list()
		if qs_type == 'question':
			for q in query_set:
				all_responses += [r.choice_clean_text for r in q.response_set.all()]
			title = str(query_set[0].question_clean_text)
			
		else:
			all_responses = [r.choice_clean_text for r in Response.objects.filter(choice_id__in=query_set.values('choice_id').distinct())]
			title = str(query_set[0].row_text)
		counter = Counter(all_responses)

		choices = list(counter.keys())
		counts = list(counter.values())

		df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
		df.rename(columns={'index': 'Choice Text', 0: 'Total'}, inplace=True)
	
		source = ColumnDataSource(data=dict(choices=choices, counts=counts, color=Viridis256[0:256:256 // len(choices)][:len(choices)]))

		p = figure(x_range=choices, y_range=(0,max(counts)*1.05), height=500, title=title,
		           toolbar_location=None, tools="hover", tooltips=('@choices: @counts'))

		p.vbar(x='choices', top='counts', width=0.9, color='color', source=source)

		p.xgrid.grid_line_color = None
		#p.legend.orientation = "horizontal"
		#p.legend.location = "top_center"
		p.xaxis.major_label_orientation = -math.pi/3

		return [components(p), df]

	def __str__(self):
		return "bar"

def get_chart_data(qs_type, query_set, query_set_2, df_qs_values):
	"""
	Helper function for generate() method of Stacked/GroupedBarChart classes

	Parameters
	----------
	* qs_type (str): the type of QuerySet we are working with
	* query_set (Django QuerySet): QuerySet of Question(s) or ResponseOption(s) to graph
	* query_set_2 (Django QuerySet): QuerySet of second Question(s) or ResponseOption(s) to graph
	* df_qs_values (list of str): the model attributes we want to extract values for from query_set

	Returns
	-------
	* df (Pandas DataFrame) -> raw data for bar chart when stacking/grouping by survey attribute
	* df0 (Pandas DataFrame) -> raw data for Question 1 (query_set) for bar chart
	* df1 (Pandas DataFrame) -> raw data for Question 2 (query_set_2) for bar chart
	* title_arg_1 (str) -> first part of chart title

	"""
	if qs_type == 'question':
		df = pd.DataFrame(Response.objects.filter(question__in=query_set).values(*df_qs_values).annotate(count=Count('choice_clean_text')))	
		df0 = pd.DataFrame(Response.objects.filter(question__in=query_set).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))
		df1 = pd.DataFrame(Response.objects.filter(question__in=query_set_2).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))
		title_arg_1 = str(query_set[0].question_clean_text)
	else:
		df = pd.DataFrame(Response.objects.filter(choice_id__in=query_set.values('choice_id').distinct()).values(*df_qs_values).annotate(count=Count('choice_clean_text')))
		df0 = pd.DataFrame(Response.objects.filter(choice_id__in=query_set.values('choice_id').distinct()).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))
		try:
			df1 = pd.DataFrame(Response.objects.filter(choice_id__in=query_set_2.values('choice_id').distinct()).values('survey__survey_year', 'survey__survey_id', 'question__question_clean_text', 'responder_id', 'choice_clean_text'))
		except:
			df1 = pd.DataFrame()
		title_arg_1 = str(query_set[0].row_text)

	return df, df0, df1, title_arg_1

def get_bokeh_data_dict(stack_group_input, survey_attribute, query_set, query_set_2, qs_type, df, df0, df1, title_arg_1, stack_group_input_1='', survey_attribute_1=''):
	"""
	Helper function for generate() method of Stacked/GroupedBarChart classes

	Parameters
	----------
	* stack_group_input (str): the survey attribute we are stacking or grouping by
		- 'court' for court
		- 'year' for year
	* survey_attribute (str): the Django-fied survey attribute we are stacking or grouping by
		- 'survey__survey_court_id' for court
		- 'survey__survey_year' for year
	* query_set (Django QuerySet): QuerySet of Question(s) or ResponseOption(s) to graph
	* query_set_2 (Django QuerySet): QuerySet of second Question(s) or ResponseOption(s) to graph
	* qs_type (str): the type of QuerySet we are working with
	* df (Pandas DataFrame): raw data for bar chart when stacking/grouping by survey attribute
	* df0 (Pandas DataFrame): raw data for Question 1 (query_set) for bar chart
	* df1 (Pandas DataFrame): raw data for Question 2 (query_set_2) for bar chart
	* title_arg_1 (str): first part of chart title
	* stack_group_input_1 (str): second survey attribute for grouping
		- default = '' (when called from StackedBarChart or GroupedBarChart)
	* survey_attribute_1 (str): the second Django-fied survey attribute we are stacking or grouping by
		- default = '' (when called from StackedBarChart or GroupedBarChart)
		- 'survey__survey_court_id' for court
		- 'survey__survey_year' for year

	Returns
	-------
	* bokeh_data_dict (dict) -> raw data for chart in dictionary form (required by Bokeh)
	* bokeh_data_df (pd.DataFrame) -> raw data for chart in DataFrame form
	* stackable_list (list) -> list of all 'relevant' columns in bokeh_data_df
		- these are the columns that become sections of bars
	* index_attribute (str) -> essentially the label for the x-axis
		- 'choice_clean_text_x' when graphing qith query_set_2
		- 'court' for court
		- 'year' for year
	* title (str) -> the title for the chart
	* y_max (int) -> maximum for y-axis of chart

	"""

	# called from stack_group_bar_chart() in views.py and we are stacking by court/year
	if stack_group_input != '':
		# when called from StackGroupBarChart, we need survey_attribute_1; otherwise, it's '', so we list comprehensify
		index = [x for x in [survey_attribute, survey_attribute_1] if x !='']
		bokeh_data_df = pd.pivot_table(df, values=['count'], index=index, columns=['choice_clean_text'])

		
		index_attribute = survey_attribute
		title = '\'{}\' vs. \'{}\''.format(title_arg_1, stack_group_input)
		if survey_attribute_1 != '':
			title += ' vs. \'{}\''.format(stack_group_input_1)
		else:
			bokeh_data_df.columns = [t[1] for t in list(bokeh_data_df.columns)]


	# called process_generate() in views.py and we are stacking by Question 2
	else:
		merged = df0.merge(df1, how='outer', on='responder_id')
		both_merged = merged[(merged['question__question_clean_text_x'].apply(lambda x: isinstance(x, str))) & (merged['question__question_clean_text_y'].apply(lambda x: isinstance(x, str)))]
		bokeh_data_df = pd.crosstab(both_merged.choice_clean_text_x, both_merged.choice_clean_text_y)
		index_attribute = 'choice_clean_text_x'
		title_arg_2 = str(query_set[1].question_clean_text) if qs_type == 'question' else str(query_set[1].row_text)
		title = "\'{}\' vs. \'{}\'".format(title_arg_1, title_arg_2)

	stackable_list = list(bokeh_data_df.columns) # we want the columns from here before we reset_index

	# case where we are calling from StackedBarChart or GroupedBarChart
	if survey_attribute_1 == '':
		bokeh_data_df.reset_index(level=[index_attribute], inplace=True)
	bokeh_data_df.fillna(0, inplace=True)

	try:
		# generate dictionary required for bokeh
		bokeh_data_dict = {c:bokeh_data_df[c].tolist() for c in bokeh_data_df.columns}
		bokeh_data_dict[index_attribute] = list(map(str, bokeh_data_dict[index_attribute])) # cast stack input to string, in case int
	except:
		pass

	y_max = bokeh_data_df[stackable_list].sum(1).max() * 1.05
	return bokeh_data_dict, bokeh_data_df, stackable_list, index_attribute, title, y_max

class GroupedBarChart:
	"""
	Class for Grouped Bar Chart

	***

	Methods
	-------
	generate(cls, query_set, query_set_2='', group_input='', *args, **kwargs) -> list: 
	"""

	@classmethod
	def generate(cls, query_set, query_set_2='', group_input='', *args, **kwargs):
		"""
		- Method called to to generate a grouped bar chart
		- Returns the HTML script/div combo required for Bokeh visualizations

		Parameters
		----------
		* query_set (Django QuerySet): QuerySet of Questions or ResponseOptions subquestions to graph
		* query_set_2 (Django QuerySet): QuerySet of second Question(s) or ResponseOption(s) to graph by
			- Required when stacking two questions
		* group_input (str): the survey attribute to group Questions or ROs by 
			- 'court' for court
			- 'year' for year'
			- only given if stacking by survey attribute
		* *args: additional, nameless parameters
		* **kwargs: additional, named parameters, namely:
			- qs_type (str): the type of QuerySet we are working with

		Returns
		-------
		[components(p), bokeh_data_df]
			* components(p) (tuple) -> (script, div), where:
				- script is HTML of script for Bokeh chart
				- div is HTML of div for Bokeh chart
			* bokeh_data_df (pd.DataFrame) -> the 'raw' data of the table

		"""
		qs_type = kwargs['qs_type']
		try: 
			survey_attribute = stack_group_mappings[group_input]
		except:
			# set to this, so we don't get error
			survey_attribute = 'survey__survey_year'

		df, df0, df1, title_arg_1 = get_chart_data(qs_type, query_set, query_set_2, [survey_attribute, 'choice_clean_text'])
		bokeh_data_dict, bokeh_data_df, stackable_list, index_attribute, title, y_max = get_bokeh_data_dict(group_input, survey_attribute, query_set, query_set_2, qs_type, df, df0, df1, title_arg_1)

		x = [ (y, response) for y in bokeh_data_dict[index_attribute] for response in stackable_list]
		counts = sum(zip(*[bokeh_data_dict[r] for r in stackable_list]), ())

		source = ColumnDataSource(data=dict(x=x, counts=counts))

		p = figure(x_range=FactorRange(*x),  y_range=(0, y_max), width=700, height=700, 
					title=title, toolbar_location=None, tools="")

		p.vbar(x='x', top='counts', width=0.9, source=source)

		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xaxis.major_label_orientation = 1
		p.xgrid.grid_line_color = None
		return [components(p), bokeh_data_df]

	def __str__(self):
		return "grouped bar"



class StackedBarChart:
	"""
	Class for Stacked Bar Chart

	***

	Methods
	-------
	generate(cls, query_set, query_set_2='', stack_input='', *args, **kwargs) -> list: 
	"""

	@classmethod
	def generate(cls, query_set, query_set_2='', stack_input='', *args, **kwargs) -> list:
		"""
		Method called to to generate a stacked bar chart

		Parameters
		----------
		* query_set (Django QuerySet): QuerySet of Questions or ResponseOptions subquestions to graph
		* query_set_2 (Django QuerySet): QuerySet of second Question(s) or ResponseOption(s) to graph by
			- Required when stacking two questions
		* stack_input (str): the survey attribute to stack Questions or ROs by 
			- 'court' for court or 'year' for year'
			- only given if stacking by survey attribute
		* *args: additional, nameless parameters
		* **kwargs: additional, named parameters, namely:
			- qs_type (str): the type of QuerySet we are working with

		Returns
		-------
		[components(p), bokeh_data_df]
			* components(p) (tuple) -> (script, div), where:
				- script is HTML of script for Bokeh chart
				- div is HTML of div for Bokeh chart
			* bokeh_data_df (pd.DataFrame) -> the 'raw' data of the table


		"""
		qs_type = kwargs['qs_type']
		try: 
			survey_attribute = stack_group_mappings[stack_input]
		except:
			# set to this, so we don't get error
			survey_attribute = 'survey__survey_year'

		df, df0, df1, title_arg_1 = get_chart_data(qs_type, query_set, query_set_2, [survey_attribute, 'choice_clean_text'])
		bokeh_data_dict, bokeh_data_df, stackable_list, index_attribute, title, y_max = get_bokeh_data_dict(stack_input, survey_attribute, query_set, query_set_2, qs_type, df, df0, df1, title_arg_1)
		


		p = figure(x_range=bokeh_data_dict[index_attribute], y_range=(0, y_max), 
					height=700, title=title, toolbar_location='right', 
					tools="hover", tooltips="$name @{}: @$name".format(index_attribute))

		p.vbar_stack(stackable_list, x=index_attribute, width=0.4,
					color=Viridis256[0:256:256 // len(stackable_list)][:len(stackable_list)], 
					source=bokeh_data_dict, legend_label=stackable_list)

		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xgrid.grid_line_color = None
		p.axis.minor_tick_line_color = None
		p.outline_line_color = None
		p.legend.location = "top_right"
		p.legend.orientation = "vertical"
		p.xaxis.major_label_orientation = -math.pi/3
		return [components(p), bokeh_data_df]

	def __str__(self):
		return "stacked bar"


class StackedGroupedBarChart:
	"""
	Class for Grouped Bar Chart

	***

	Methods
	-------
	generate(cls, query_set, query_set_2='', stack_input='', group_input='', *args, **kwargs) -> list: 
	"""

	@classmethod
	def generate(cls, query_set, query_set_2='', stack_input='', group_input='', *args, **kwargs):
		"""
		Method called to to generate a stacked bar chart

		Parameters
		----------
		* query_set (Django QuerySet): QuerySet of Questions or ResponseOptions subquestions to graph
		* query_set_2 (Django QuerySet): QuerySet of second Question(s) or ResponseOption(s) to graph by
			- Required when stacking two questions
		* stack_input (str): the survey attribute to stack Questions or ROs by 
			- 'court' for court or 'year' for year'
			- only given if stacking by survey attribute
		* group_input (str): the survey attribute to group Questions or ROs by 
			- 'court' for court
			- 'year' for year'
		* *args: additional, nameless parameters
		* **kwargs: additional, named parameters, namely:
			- qs_type (str): the type of QuerySet we are working with

		Returns
		-------
		[components(p), bokeh_data_df]
			* components(p) (tuple) -> (script, div), where:
				- script is HTML of script for Bokeh chart
				- div is HTML of div for Bokeh chart
			* bokeh_data_df (pd.DataFrame) -> the 'raw' data of the table


		"""
		qs_type = kwargs['qs_type']
		stack_survey_attribute = stack_group_mappings[stack_input]
		group_survey_attribute = stack_group_mappings[group_input]

		df, df0, df1, title_arg_1 = get_chart_data(qs_type, query_set, query_set_2, [stack_survey_attribute, group_survey_attribute, 'choice_clean_text'])
		bokeh_data_dict, bokeh_data_df, stackable_list, index_attribute, title, y_max = get_bokeh_data_dict(stack_input, stack_survey_attribute, query_set, query_set_2, qs_type, df, df0, df1, title_arg_1, group_input, group_survey_attribute)


		factors = list(bokeh_data_df.index)
		
		factors = [(str(t[0]), str(t[1])) for t in factors] # cast all elements of factors to strings

		bokeh_data_df.columns = bokeh_data_df.columns.get_level_values(1)
		bokeh_data_df.fillna(0, inplace=True)
		data = {'x': factors}
		for c in bokeh_data_df.columns:
			data[c] = bokeh_data_df[c].tolist()
		source = ColumnDataSource(data=data)
		p = figure(x_range=FactorRange(*factors), y_range=(0, bokeh_data_df.sum(1).max() * 1.05), 
			height=700)
		p.vbar_stack(list(map(str, bokeh_data_df.columns)), x='x', width=0.9, alpha=0.5, color=Viridis256[0:256:256 // len(bokeh_data_df.columns)][:len(bokeh_data_df.columns)], 
			source=source, legend_label=list(map(str, bokeh_data_df.columns)))

		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xaxis.major_label_orientation = 1
		p.xgrid.grid_line_color = None
		p.legend.location = "top_right"
		p.legend.orientation = "vertical"
		return [components(p), bokeh_data_df]
	def __str__(self):
		return "stacked grouped bar"

class PieChart:
	@classmethod
	def generate(cls, query_set, *args, **kwargs):
		"""
		Method called to to generate a stacked bar chart

		Parameters
		----------
		* query_set (Django QuerySet): QuerySet of Questions or ResponseOptions subquestions to graph
		* query_set_2 (Django QuerySet): QuerySet of second Question(s) or ResponseOption(s) to graph by
			- Required when stacking two questions
		* stack_input (str): the survey attribute to stack Questions or ROs by 
			- 'court' for court or 'year' for year'
			- only given if stacking by survey attribute
		* group_input (str): the survey attribute to group Questions or ROs by 
			- 'court' for court
			- 'year' for year'
		* *args: additional, nameless parameters
		* **kwargs: additional, named parameters, namely:
			- qs_type (str): the type of QuerySet we are working with

		Returns
		-------
		[components(p), bokeh_data_df]
			* components(p) (tuple) -> (script, div), where:
				- script is HTML of script for Bokeh chart
				- div is HTML of div for Bokeh chart
			* bokeh_data_df (pd.DataFrame) -> the 'raw' data of the table


		"""

		qs_type = kwargs['qs_type']
		all_responses = list()
		if qs_type == 'question':
			for q in query_set:
				all_responses += [r.choice_clean_text for r in q.response_set.all()]
			title = str(query_set[0].question_clean_text)
			
		else:
			all_responses = [r.choice_clean_text for r in Response.objects.filter(choice_id__in=query_set.values('choice_id').distinct())]
			title = str(query_set[0].row_text)
		counter = Counter(all_responses)

		df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
		df.rename(columns={'index': 'Choice Text', 0: 'Total'}, inplace=True)

		data = pd.Series(counter).reset_index(name="value").rename(columns={'index': 'response'})
		data['angle'] = data['value']/data['value'].sum() * 2*math.pi
		data['percentage'] = (data['value']/data['value'].sum() / 100) * 360

		data['color'] = Category20c[len(counter)]
		plot2 = figure(height=350, title=title, 
		toolbar_location=None, tools="hover", tooltips=[('Total','@value')], x_range=(-0.5, 1.0))

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

class ScatterPlot: #can be used for categorical variables with continuous values; eg time
	#ColumnDataSource takes in pandas dataframe....not sure which variable that is
	@classmethod
	def generate(cls, question_query_set, *args, **kwargs):
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
		 toolbar_location=None, tools="hover", tooltips=[('Total','@value')], sizing_mode="stretch_width")

		plot.circle(x="choice", y=jitter("count", width=0.6, range=plot.y_range), source=comdata, alpha=0.3)

		# plot2 = figure(title=str(question_query_set[0]), tools="hover")
		# plot2.xaxis.axis_label = "x-axis"
		# plot2.yaxis.axis_label = "y-axis"
		# plot2.scatter(choices, counts)

		script1, div1 = components(plot)

		return components(plot)

	def __str__(self):
		return "scatter"

class HeatMap:
	@classmethod
	def generate(cls, question_query_set, **kwargs):
		return

	def __str__(self):
		return "heatmap"

class BoxPlot:
	@classmethod
	def generate(cls, question_query_set, **kwargs):
		return 

	def __str__(self):
		return "boxplot"

class LineGraph:
	@classmethod
	def generate(cls, question_query_set, **kwargs):
		return 

	def __str__(self):
		return "line"

class Counter_Table:
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

		df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
		df.rename(columns={'index': 'Choice Text', 0: 'Total'}, inplace=True)

		#show(data_table)
		return [components(data_table), df]

	def __str__(self):
		return "table"
		

def determine_valid_graph_types(question_type_subtype_tuple):
	''' Returns list of valid graph types given a tuple of form (question_type, question_subtype) '''
	question_type_subtype_graph_type_mapping = {
								('single_choice', 'vertical'): [BarChart(), PieChart(), StackedBarChart(), GroupedBarChart()],
								('open_ended', 'essay'): [],
								('open_ended', 'single'): [],
								('multiple_choice', 'vertical'): [BarChart(), PieChart(), StackedBarChart(), GroupedBarChart()],
								('open_ended', 'numerical'): [],
								('single_choice', 'vertical_two_col'): [],
								('open_ended', 'multi'): [],
								('matrix', 'single'): [BarChart(), PieChart(), StackedBarChart()],
								('matrix', 'rating'): [],
								('datetime', 'time_only'): [ScatterPlot()],
								('single_choice', 'menu'): [],
								('datetime', 'date_only'): []
	}

	return question_type_subtype_graph_type_mapping[question_type_subtype_tuple]
