'''

This file takes in a DataFrame of new questions to be uploaded and does the following:

	1) Cleans the question_text field of the DataFrame (prior to uploading to database)
	2) Performs cosine similarity algorithm on questions to find which questions it is similar to
		- Makes a new entry in the question_id_mappings dictionary of question_id_mappings.py for the new questions

'''