from collections import Counter

def determine_valid_graph_types(question_type_subtype_tuple):
	''' Returns list of valid graph types given a tuple of form (question_type, question_subtype) '''
	question_type_subtype_graph_type_mapping = {
								('single_choice', 'vertical'): ['bar', 'pie'],
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




