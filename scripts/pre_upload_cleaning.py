import numpy as np

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


def clean_func(ind, question_id, question_ids, response_text):
	#print(ind, response_text)
	new_response_text = response_text
	if question_id in question_ids:
		if type(response_text) == str:
			match = re.search(r'(\d+)', response_text)
			if match:
				new_response_text = match.group(1)
			else:
				return np.nan
		else:
			return np.nan
	return new_response_text