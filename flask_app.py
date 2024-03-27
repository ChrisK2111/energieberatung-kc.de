from flask import Flask, render_template, jsonify, session, send_file, request
from flask_mail import Mail, Message
import random
import json
from datetime import datetime
from py.sfp_app import calc_sfp, final_cond_card, sfp_cards, initial_cond_card


app = Flask(__name__,static_url_path='',
            static_folder='static',)
app.secret_key = 'a#130u#98bm_23j30_bas9'

app.config['MAIL_SERVER'] = 'smtp.strato.de'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'info@energieberatung-kc.de'
app.config['MAIL_PASSWORD'] = 'chrzebrzeszczyna'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/mountain')
def mountain():
    mountains = ['Everest', 'K2', 'Kilimanjaro']
    return render_template('mountain.html', mountain=mountains)

@app.route('/mountain/<mt>')
def specific_mountain(mt):
    return "This is a big mountain: " + str(mt)


@app.route('/')
def index():
    init_session()
    return render_template('index.html')

@app.route('/agb')
def agb():
    return render_template('legal/agb.html')

@app.route('/dsgvo')
def dsgvo():
    return render_template('legal/dsgvo.html')

@app.route('/impressum')
def impressum():
    return render_template('legal/impressum.html')

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
    init_session()
    return render_template('kontakt/index.html')

@app.route('/kontakt', methods=['POST'])
def contact_form_submitted():

    session['contact_form_submitted'] = True
    for key in request.form.keys():
            ext_key = "contact_form_" + key
            session[ext_key] = request.form.get(key);
    
    # JSON-String in JSON-Datei schreiben
    with open(file_path, 'a') as file:
        json.dump(session, file)
        file.write('\n')
    # send_mail()

    return render_template('kontakt/success.html')


def send_mail():
    msg = Message("Anfrage erhalten", sender="info@energieberatung-kc.de", recipients=[session['contact_form_email']])
    msg.body = "Guten Tag " + session['contact_form_firstName'] + " " + session['contact_form_lastName'] + ",\n"\
                "vielen Dank für Ihre Anfrage. Ich werde mich umgehend bei Ihnen melden.\n" \
                "\n"\
                "Mit freundlichen Grüßen\n"\
                "Christian Karczewski" 
    mail.send(msg)

    msg = Message("Anfrage erhalten", sender="info@energieberatung-kc.de", recipients=["christian.karczewski@yahoo.de"])
    msg.body = "Guten Tag Christian Karczewski, \n" \
                "es ist eine neue Anfrage von " + session['contact_form_firstName'] + " " + session['contact_form_lastName'] + " aus " + session['contact_form_city'] + " eingegangen.\n"\
                "Die Emailadresse lautet: " + session['contact_form_email'] + "\n" \
                "Die Nachricht lautet:\n" \
                "--------------------- \n" + \
                session["contact_form_message"] + "\n" \
                "---------------------\n\n" + \
                "Mit freundlichen Grüßen\n" \
                "Christian Karczewski" 
    mail.send(msg)

    return "Sent Mail"



def init_session():
    if not('ids' in session):
        session['ids'] = random.randint(0,int(1e10))
    return True

file_path = 'data.json'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001,debug=True)
