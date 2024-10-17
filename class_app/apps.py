from django.apps import AppConfig
from flask import Flask, render_template, request
import datetime


class ClassConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'class_app'


app = Flask(__name__)

# Initialize a list to store announcements
announcements = []

@app.route('/')
def index():
    current_date = datetime.date.today().strftime("%B %d, %Y")  # Get current date in a readable format
    return render_template('index.html', announcements=announcements, current_date=current_date)

@app.route('/add_announcement', methods=['POST'])
def add_announcement():
    announcement_text = request.form['announcement']
    current_time = datetime.datetime.now().strftime("%H:%M")
    # Insert the new announcement at the beginning of the list
    announcements.insert(0, {'text': announcement_text, 'time': current_time})

    return index()

@app.route('/clear_announcements', methods=['POST'])
def clear_announcements():
    global announcements
    announcements.clear()  # Clear all announcements
    return index()

if __name__ == '__main__':
    app.run(debug=True)