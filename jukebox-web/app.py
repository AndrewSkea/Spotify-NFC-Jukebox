from multiprocessing import Pool, context
from multiprocessing.context import TimeoutError
import time
from flask import Flask, render_template, Response, jsonify

from utils import timeout

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UERAIJFajjdlierjlefwkfjelmm982374EFA'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

global pool_result

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] =  "POST, GET, PUT, OPTIONS"
    return response


@timeout(10)
def worker(spotify_uri):
    print('Starting {}'.format(spotify_uri))
    time.sleep(5)
    print("Done: {}".format(spotify_uri))
    return spotify_uri


@app.route("/check-write-progress", methods=['GET'])
def check_progress():
    status_resp = "Place RFID Card on Reader"
    if pool_result.ready():
        try:
            ret = pool_result.get(timeout=1)[0]
            if ret is not None:
                status_resp = "Written {} to RFID card".format(ret)
        except context.TimeoutError:
            status_resp = "Write operation has timed out!"
    return jsonify({"status": status_resp})

@app.route('/write-uri/<spotify_uri>', methods=['POST'])
def write_uri(spotify_uri):
    pool = Pool()
    global pool_result
    pool_result = pool.map_async(worker, [spotify_uri])
    return Response("{'status':'started'}", status=202, mimetype='application/json')


def update_spotify_auth(username, password):
    lines = open('/etc/default/raspotify').read().splitlines()
    line_to_rep = None
    for i, line in enumerate(lines):
        print(line)
        if line.startswith("OPTIONS"):
            print(line)
            line_to_rep = i
    lines[i-1] = "OPTIONS=\" --username andrewnew --passord dkfjsalkdjfksdj\""
    open('/etc/default/raspotify','w').write('\n'.join(lines))


@app.route('/', methods=['GET'])
def sessions():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
