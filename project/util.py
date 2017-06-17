import datetime

def get_output_filename():
	date_str =  datetime.date.today().strftime('%Y-%m-%d')
	return 'all_results_%s.csv' % date_str
	