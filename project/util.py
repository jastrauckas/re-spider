import datetime

# output firectory for file storage 
output_dir = 'listing_history'

today = datetime.date.today()

def get_output_filename(date=today):
	date_str =  date.strftime('%Y-%m-%d')
	return '%s/all_results_%s.csv' % (output_dir, date_str)

def get_yesterday_results():
	results = []
	yesterday = datetime.date.today() - datetime.timedelta(days=1)
	history_filename = get_output_filename(yesterday)
	with open(history_filename, 'r') as history_file:
		for line in history_file:
			results.append(line.rstrip('\n')) 

	return results

	