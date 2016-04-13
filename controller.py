import logging, os, model, view
from flask import Flask

app = Flask(__name__)

# Set up logging for everyone
def configure_logger():

    # Log to file
    logging.basicConfig(filename='gcplot.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


# Controller calls View
@app.route('/user/<username>/graph', methods=['GET', 'POST'])
def graph(username):

	activities = model.get_activities(os.path.join('cache', username))
	return view.show_graph(activities, model.get_list_of_available_data(os.path.join('cache', username)), username)

@app.route('/user/<username>/activities')
def activities(username):
	activities = model.get_activities(os.path.join('cache', username))
	return view.show_activities(activities, username)

if __name__ == '__main__':

	configure_logger()
	#model.sync_data_with_gc()
	app.run(debug=True)