from flask import render_template, request
from pandas_highcharts.core import serialize, _pd2hc_kind
import pandas
import model
import gcplot
import tempfile
import logging
import os

# Available types : "bar": "column", "barh": "bar", "area": "area", "line": "line", "pie": "pie"
# Expects a Pandas serie
def gen_highcharts_json(data, title, kind='bar', pandas_highcharts=True):

	if pandas_highcharts:
		json = serialize(data, output_type='json', title=title, kind=kind, fontsize='12', grid=True, legend=False)
	else:
		json = '{"title":{"text":"'+title+'"},"series":[{"data":['
		for index, value in data.iteritems():
			json += '["{}",{}],'.format(str(index), value)
		json = json[:-1]
		json += '],"name":"'+str(data.name[0])+'","yAxis":0,"marker":{"enabled":true,"radius":3},shadow : true,}],"yAxis":[{"labels":{"style":{"fontSize":"12"}},"gridLineDashStyle":"Dot","gridLineWidth":1}],"chart":{"type":"'+_pd2hc_kind[kind]+'"},"xAxis":{"labels":{"style":{"fontSize":"12"}},"gridLineDashStyle":"Dot","categories":['
		for index, _ in data.iteritems():
			json += '"{}",'.format(str(index))
		json = json[:-1]
		json += '],"gridLineWidth":1},"legend":{"enabled":false},"credits":false}'

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

def import_code_from_string(code, name, add_to_sys_modules=0):
	import sys,imp
	module = imp.new_module(name)
	exec code in module.__dict__
	if add_to_sys_modules:
		sys.modules[name] = module
	return module


def show_graph(gc_user_dir, data_list, username):

	# Get the field to draw from the form on the template
	data_field = request.form.get('fields')
	if data_field:
		data_to_plot = str(data_field)
	else:
		# default one
		data_to_plot = 'average_heart_rate_bpm'

	# Get the plot type from the form on the template
	plot_type = request.form.get('type')
	if plot_type:
		plot_type = str(plot_type)
	else:
		# default one
		plot_type = 'line'

	# Filter results
	#filters = {"average_heart_rate_bpm > 140", "average_heart_rate_bpm < 200"}
	#for filt in filters:
#
#	#	filter_code = \
#	#	"""
#def #filter_func(series):
#	#return series[series.""" + filt + """]
#	#	"""
#
#	#	# Test code beforehand
#	#	try:
#	#		compile(filter_code, os.path.join(tempfile.mkdtemp(), "bogus.py"), "exec")
#	#	except Exception as e:
#	#		logging.error("Error {} compiling {}".format(e, filter_code))
#	#		continue
#
#	#	filter_module = import_code_from_string(filter_code, "test")
	#	activities = filter_module.filter_func(activities)

	# Get data
	data_series = model.get_data_series(gc_user_dir, data_to_plot)

	# Serialize and output to webpage
	series = gen_highcharts_json(data_series, data_list[data_to_plot], kind=plot_type, pandas_highcharts=False)
	return render_template('graph.html', chart='my-chart', data=series, options=data_list, current_data=data_to_plot, username=username)

def show_bar(data, data_list, username):

	# Get the field to draw from the form on the template
	data_field = request.form.get('fields')
	if data_field:
		data_to_plot = str(data_field)
	else:
		data_to_plot = 'average_heart_rate_bpm'

	# Only keep the data we want to transfer to the template
	data_series = data

	# Serialize and output to webpage
	json_data = gen_highcharts_json(data_series, data_list[data_to_plot], 'bar', False)
	return render_template('graph.html', chart='my-chart', data=json_data, options=data_list, current_data=data_to_plot, username=username)