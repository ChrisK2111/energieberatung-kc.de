from flask import Flask, render_template, jsonify, session, send_file, request
import random
import json
from datetime import datetime
from py.sfp_app import calc_sfp, final_cond_card, sfp_cards, initial_cond_card


app = Flask(__name__,static_url_path='',
            static_folder='static',)
app.secret_key = 'a#130u#98bm_23j30_bas9'

@app.route('/mountain')
def mountain():
    mountains = ['Everest', 'K2', 'Kilimanjaro']
    return render_template('mountain.html', mountain=mountains)

@app.route('/mountain/<mt>')
def specific_mountain(mt):
    return "This is a big mountain: " + str(mt)

@app.route('/py/firstAPI')
def firstAPI():
    data = {'message': 'Hello, World!'}
    return jsonify(data)

@app.route('/')
def index():
    init_session()
    return render_template('index.html')

@app.route('/sfp')
def sfp():
    init_session()
    if 'button_clicked' in session:
        rf_data = calc_sfp(session)
        txt_ini_card = initial_cond_card(rf_data)
        txt_final_card = final_cond_card(rf_data)
        rf_cards = sfp_cards(rf_data)
        t = render_template('sfp/index.html',session=session, txt_ini_card=txt_ini_card, txt_final_card=txt_final_card,cards=rf_cards)
    else:
        t = render_template('sfp/index.html',session=session);
    return t

@app.route('/sfp', methods=['POST'])
def update_sfp():
    if request.method == 'POST':
        session['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session['button_clicked'] = True
        if 'check_basementInsulation' in session:
            session.pop('check_basementInsulation')
        for key in request.form.keys():
            session[key] = request.form.get(key);

        # JSON-String in JSON-Datei schreiben
        with open(file_path, 'a') as file:
            json.dump(session, file)
            file.write('\n')
        
        rf_data = calc_sfp(session)
        txt_ini_card = initial_cond_card(rf_data)
        txt_final_card = final_cond_card(rf_data)
        rf_cards = sfp_cards(rf_data)

    return render_template('sfp/index.html',session=session, txt_ini_card=txt_ini_card, txt_final_card=txt_final_card,cards=rf_cards)

@app.route('/get_sfp_data', methods=['GET'])
def send_sfp_data():
    if request.method == 'GET':
        if 'button_clicked' in session.keys():
            rf_data = calc_sfp(session)
        else:
            rf_data = None
    return jsonify(rf_data)

@app.route('/kontakt')
def kontakt():
    return render_template('kontakt/index.html')

def init_session():
    if not('ids' in session):
        session['ids'] = random.randint(0,int(1e10))
    return True

file_path = 'data.json'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001,debug=True)
