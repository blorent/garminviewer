import gcplot
from gcexport import gc_sync
import os

def get_list_of_available_data(gc_user_dir):
	available_fields = gcplot.get_numeric_data_list(os.path.join(gc_user_dir, 'activities.csv'))
	fields_dict = {f : gcplot.get_human_readable_name(f) for f in available_fields}
	return fields_dict

def get_activities(gc_user_dir):
	activities = gcplot.get_activities(os.path.join(gc_user_dir, 'activities.csv'))
	return activities
	

def get_data(activities, series_names):

	# Only keep what we want to plot, and filter out NaNs
	filtered_activities = activities[series_names].dropna()

	# Set human readable names
	filtered_activities.index.name = "Date"
	for serie_name in series_names:
		filtered_activities = filtered_activities.rename(columns={serie_name: gcplot.get_human_readable_name(serie_name)})

	return filtered_activities

def sync_data_with_gc(gc_user_dir):

	gc_sync('***', '***', 'all', 'tcx', gc_user_dir, False)
