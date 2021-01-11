from flask import Flask, render_template, Response
import time, math
import sys
from .utils import timeout, write_spotify_uri, read_spotify_uri

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f288841f27567d441f2b6176a'

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] =  "POST, GET, PUT, OPTIONS"
    return response


@app.route('/read-uri')
def read_uri(spotify_uri):
    try:
        cid, text = read_spotify_uri()
        return Response("{'status':'complete', 'id':'{}', 'text': '{}'}".format(cid, text), status=200, mimetype='application/json')
    except TimeoutError:
        return Response("{'status':'timed_out'}", status=408, mimetype='application/json')


@app.route('/write-uri/<spotify_uri>')
def write_uri(spotify_uri):
    try:
        write_spotify_uri(spotify_uri)
        return Response("{'status':'complete'}", status=200, mimetype='application/json')
    except TimeoutError:
        return Response("{'status':'timed_out'}", status=408, mimetype='application/json')


@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)