from flask import Blueprint,render_template

welcome = Blueprint('welcome',__name__)




@welcome.route('/welcome')
def show():
	return render_template('welcome.html')