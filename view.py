from flask import render_template
from pandas_highcharts.core import serialize
import pandas
import model

def show_activities(activities, username):

	# Format properly
	for index, row in activities.iterrows():

		# We want 'Distance' to show as 'xx km'
		if row.distance.startswith('0.00'):
			activities.loc[index, 'distance'] = '-'
		else:
			activities.loc[index, 'distance'] = row.distance.split(' ')[0] + ' km'

		# We want 'HR' to show as int without decimal, and ignore NaNs
		if str(row.max_heart_rate_bpm) == "nan":
			activities.loc[index, 'max_heart_rate_bpm'] = "-"
		else:
			activities.loc[index, 'max_heart_rate_bpm'] = str(row.max_heart_rate_bpm).split('.')[0]

		if str(row.max_heart_rate_bpm) == "nan":
			activities.loc[index, 'min_heart_rate_bpm'] = "-"
		else:
			activities.loc[index, 'min_heart_rate_bpm'] = str(row.min_heart_rate_bpm).split('.')[0]

		if str(row.max_heart_rate_bpm) == "nan":
			activities.loc[index, 'average_heart_rate_bpm'] = "-"
		else:
			activities.loc[index, 'average_heart_rate_bpm'] = str(row.average_heart_rate_bpm).split('.')[0]

		# We want speed to show as min/km and ignore Nans
		if '0.0' in str(row.average_speed):
			activities.loc[index, 'average_speed'] = '-'
		else:
			activities.loc[index, 'average_speed'] = str(row.average_speed).split(' ')[0]
		
		if 'nan' in str(row.max_speed):
			activities.loc[index, 'max_speed'] = '-'
		else:
			activities.loc[index, 'max_speed'] = str(row.max_speed)

	# Convert to list for easy iterating in template
	l = list(activities.itertuples(index=False))

	return render_template('activities.html', data=l, username=username)

def show_graph(data_series, data_to_plot, data_list, username):

	# Filter results
	data_series = data_series[int(data_series.average_heart_rate_bpm) > 125]

	# Serialize and output to webpage
	series = serialize(data_series, output_type='json', title=data_list[data_to_plot], kind="line", fontsize='12', grid=True, legend=False)
	return render_template('graph.html', chart='my-chart', data=series, options=data_list, current_data=data_to_plot, username=username)