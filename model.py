import gcplot
from gcexport import gc_sync
import os
import pandas as pd

computed_fields = {'distance_per_week':'Distance per week', 'distance_per_month':'Distance per month'}

def get_list_of_available_data(gc_user_dir):

	# Get the data directly from activities list
	available_fields = gcplot.get_numeric_data_list(os.path.join(gc_user_dir, 'activities.csv'))
	fields_dict = {f : gcplot.get_human_readable_name(f) for f in available_fields}

	# Add processed data
	fields_dict.update(computed_fields)

	return fields_dict

def get_data_series(gc_user_dir, data_series_name):

	activities_df = gcplot.get_activities(os.path.join(gc_user_dir, 'activities.csv'))
	
	# First handle the default ones
	if data_series_name not in computed_fields:
		s = activities_df[data_series_name].dropna()
		s.rename("data_series_name")
		return s
	# Then the computed ones
	else:
		distance_per_week, distance_per_month = compute_cumulated_distance(activities_df)
		if data_series_name == 'distance_per_week':
			return distance_per_week.dropna()
		elif data_series_name == 'distance_per_month':
			return distance_per_month.dropna()
		else:
			return None


def get_activities(gc_user_dir):
	activities = gcplot.get_activities(os.path.join(gc_user_dir, 'activities.csv'))
	return activities
	
def sync_data_with_gc(gc_user_dir):

	gc_sync('***', '***', 'all', 'tcx', gc_user_dir, False)


def compute_cumulated_distance(activities_df):

	# init counters
	current_week = 0
	current_month = 0
	current_week_total = 0.0
	current_month_total = 0.0
	week_data = pd.Series()
	month_data = pd.Series()

	# iterate over activities and compute total per week and month
	for index, row in activities_df.iterrows():

		week = row.begin_timestamp.year * 100 + row.begin_timestamp.isocalendar()[1]
		month = row.begin_timestamp.year * 100 + row.begin_timestamp.month

		# Populate the week dataframe
		if week == current_week:
			# add to the curent total
			current_week_total += float(row.distance_raw)
		else:
			# record if any data
			if current_week_total != 0.0:			
				new_data = pd.Series([current_week_total], name=['distance'], index=[str(current_month)[:4]+"."+str(current_month)[-2:]])
				week_data = week_data.append(new_data)

			# switch to next month
			current_week = week

			# init the curent total
			current_week_total = float(row.distance_raw)

		# Populate the month dataframe
		if month == current_month:
			# add to the curent total
			current_month_total += float(row.distance_raw)
		else:
			# record if any data
			if current_month_total != 0.0:
				new_data = pd.Series([current_month_total], name=['distance'], index=[str(current_month)[-2:]+"/"+str(current_month)[:4]])
				month_data = month_data.append(new_data)

			# switch to next month
			current_month = month

			# init the curent total
			current_month_total = float(row.distance_raw)

	# record ongoing week if any data
	if current_week_total != 0.0:
		new_data = pd.Series([current_week_total], name=['distance'], index=[str(current_month)[:4]+"."+str(current_month)[-2:]])
		week_data = week_data.append(new_data)

	# record ongoing month if any data
	if current_month_total != 0.0:
		new_data = pd.Series([current_month_total], name=['distance'], index=[str(current_month)[-2:]+"/"+str(current_month)[:4]])
		month_data = month_data.append(new_data)

	# We want int, not float for totals
	week_data = week_data.astype(int)
	month_data = month_data.astype(int)

	return week_data, month_data

if __name__ == '__main__':

	week_df, month_df = compute_cumulated_distance(os.path.join('cache', 'blorent'))
	#print(week_df)
	print(month_df)