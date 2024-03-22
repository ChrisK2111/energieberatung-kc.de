from flask import Flask, render_template, jsonify, session, send_file, request
import random

app = Flask(__name__)
app.secret_key = 'a#130u#98bm_23j30_bas9'

@app.route('/mountain')
def index():
    mountains = ['Everest', 'K2', 'Kilimanjaro']
    return render_template('mountain.html', mountain=mountains)

@app.route('/mountain/<mt>')
def mountain(mt):
    return "This is a big mountain: " + str(mt)

@app.route('/py/firstAPI')
def firstAPI():
    data = {'message': 'Hello, World!'}
    return jsonify(data)

@app.route('/')
def init_session():
    if not('ids' in session):
        session['ids'] = random.randint(0,int(1e10))
    return render_template('index.html')

@app.route('/sfp')
def sfp():
    return render_template('sfp/index.html')

@app.route('/sfp', methods=['POST'])
def update_sfp():
    print(1)
    return render_template('sfp/index.html')


@app.route('/kontakt')
def kontakt():
    return render_template('kontakt/index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001,debug=True)
