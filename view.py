from flask import render_template, request
from pandas_highcharts.core import serialize, _pd2hc_kind
import pandas
import model
import gcplot
import logging
import os

# Available types : "bar": "column", "barh": "bar", "area": "area", "line": "line", "pie": "pie"
# Expects a Pandas serie
def gen_highcharts_json(data, title, x_axis=None, kind='line', pandas_highcharts=True):

	if pandas_highcharts:
		json = serialize(data, output_type='json', title=title, kind=kind, fontsize='12', grid=True, legend=False)
	else:
		# define index type
		print(data)
		print(data.index)
		print(data.index.dtype)
		if data.index.dtype == 'datetime64[ns]':
			x_axis_type = 'datetime'
		else:
			x_axis_type = 'category'

		print(x_axis_type)

		json = """{
	title: {
		text: '"""+title+"""'
	},
	xAxis: {
		type: '"""+x_axis_type+"""'
	},
	yAxis: {
		title: {
			text: '"""+title+"""'
		}
	},
	legend: {
		enabled: false
	},
	credits: false,
	plotOptions: {
	    line: {
	        marker: {
	        	enabled: null,
	            radius: 3
	        },
	        lineWidth: 2,
	        states: {
	            hover: {
	                lineWidth: 2
	            }
	        },
	        threshold: null
	    }
    },
	series: [{
		type : '"""+kind+"""',
		data: ["""
		for index, value in data.iteritems():
			if x_axis_type == 'datetime':
				json += '[Date.UTC({}, {}, {}),{}],'.format(str(index)[0:4], str(index)[5:7], str(index)[8:10], value)
			else:
				json += '["{}",{}],'.format(str(index), value)
		json = json[:-1]
		json+= """]
	}]
}
	"""

	print(json)

	return json


def show_activities(activities, username):

	# Format properly
	for index, row in activities.iterrows():

		# We want 'Distance' to show as 'xx km'
		if row.distance.startswith('0.00'):
			activities.loc[index, 'distance'] = '-'
		else:
			activities.loc[index, 'distance'] = row.distance.split(' ')[0] + ' km'

		# We want 'Description' to be a string always
		if "nan" in str(row.description):
			activities.loc[index, 'description'] = "-"
		else:
			activities.loc[index, 'description'] = str(row.description)

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


def show_stats(gc_user_dir, data_list, username):

	# Get the field to draw from the form on the template
	data_field = request.form.get('fields')
	if data_field:
		data_to_plot = str(data_field)
	else:
		# default one
		data_to_plot = 'average_heart_rate_bpm'

	# Get the plot type from the form on the template
	plot_type = request.form.get('plot_type')
	if plot_type:
		plot_type = str(plot_type)
	else:
		# default one
		plot_type = 'line'

	# get the filters, if any
	filter_fields = request.form.get('filter_field[]')

	# Get data
	#filters = {"average_heart_rate_bpm > 140", "average_heart_rate_bpm < 200"}
	data_series = model.get_data_series(gc_user_dir, data_to_plot, None)

	week_total, month_total = model.compute_cumulated_distances(model.get_activities(gc_user_dir))
	highcharts_json = gen_highcharts_json(month_total, 'Distance per month', kind='column', pandas_highcharts=False)

	# Serialize and output to webpage
	#highcharts_json = gen_highcharts_json(data_series, data_list[data_to_plot], kind=plot_type, pandas_highcharts=False)
	return render_template('graph.html', chart='my-chart', highcharts_code=highcharts_json, options=data_list, current_data=data_to_plot, current_plot_type=plot_type,  username=username)
