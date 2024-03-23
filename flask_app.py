from flask import Flask, render_template, jsonify, session, send_file, request
import random
import json
from datetime import datetime
from py.sfp_app import calc_sfp


app = Flask(__name__,static_url_path='',
            static_folder='static',)
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
    if request.method == 'POST':
        sfp_form = {'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  'ids': session['ids']}
        for key in request.form.keys():
            sfp_form[key] = request.form.get(key)

        # JSON-String in JSON-Datei schreiben
        with open(file_path, 'a') as file:
            json.dump(sfp_form, file)
            file.write('\n')
        

        q_net = calc_sfp(sfp_form)

    return jsonify(q_net)


@app.route('/kontakt')
def kontakt():
    return render_template('kontakt/index.html')



file_path = 'data.json'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001,debug=True)
