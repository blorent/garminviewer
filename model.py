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
	
def sync_data_with_gc(gc_user_dir):

	gc_sync('***', '***', 'all', 'tcx', gc_user_dir, False)
