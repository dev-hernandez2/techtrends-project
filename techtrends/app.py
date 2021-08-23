import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`

total_connections = 0

def get_db_connection():
    global total_connections
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    total_connections = total_connections +1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info('Home page request retrieved successfull')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:

        app.logger.error('A non-existing article is accessed and a 404 page is returned')
        return render_template('404.html'), 404
    else:
       
        app.logger.info('Article "%s" retrieved!', post['title'])
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    app.logger.info('About page request retrieved successfull')
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            
            app.logger.info('A new article "%s" is created!', title)

            return redirect(url_for('index'))

    app.logger.info('Create page request successfull')
    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )

    app.logger.info('Application health request successfull')
    return response


# Metric endpint functionality
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    response = app.response_class(
        response=json.dumps(
            {
                "post_count": len(posts), 
                "db_connection_count": total_connections
            }),
        status=200,
        mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')

    return response


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout), logging.StreamHandler(sys.stderr)])
    app.run(host='0.0.0.0', port='3111')
