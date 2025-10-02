from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mandir.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------ DATABASE MODELS ------------------
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

class Mantra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    text = db.Column(db.Text)
    deity = db.Column(db.String(100))

class Aarti(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    title = db.Column(db.String(200))
    text = db.Column(db.Text)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    amount = db.Column(db.Float)
    payment_status = db.Column(db.String(50), default="Success")

# ------------------ PRE-LOADED CONTENT ------------------
def preload_content():
    if not Mantra.query.first():
        mantras = [
            {"title":"Gayatri Mantra", "deity":"Savitar", "text":"ॐ भूर् भुवः स्वः । तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि । धियो यो नः प्रचोदयात् ॥"},
            {"title":"Mahamrityunjaya Mantra", "deity":"Shiva", "text":"ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्। उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात्॥"},
            {"title":"Hanuman Mantra", "deity":"Hanuman", "text":"ॐ हनुमते नमः।"},
            {"title":"Shiv Mantra", "deity":"Shiva", "text":"ॐ नमः शिवाय।"},
        ]
        for m in mantras:
            db.session.add(Mantra(title=m["title"], deity=m["deity"], text=m["text"]))
        db.session.commit()

    if not Aarti.query.first():
        aartis = [
            {"title":"Ganesh Aarti", "text":"जय गणेश जय गणेश जय गणपति देवा। माता जाकी पार्वती पिता महादेवा॥"},
            {"title":"Shiva Aarti", "text":"जय शिव ओंकारा, भोलेनाथ की जय।"},
            {"title":"Hanuman Aarti", "text":"जय हनुमान ज्ञान गुन सागर। जय कपीस तिहुँ लोक उजागर॥"},
        ]
        for a in aartis:
            db.session.add(Aarti(title=a["title"], text=a["text"]))
        db.session.commit()

# ------------------ ROUTES ------------------
@app.route('/')
def home():
    today_aarti = Aarti.query.order_by(Aarti.date.desc()).first()
    return render_template('home.html', aarti=today_aarti)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        db.session.add(Contact(name=name,email=email,message=message))
        db.session.commit()
        return redirect('/')
    return render_template('contact.html')

@app.route('/mantra', methods=['GET','POST'])
def mantra():
    results = Mantra.query.all()
    if request.method == 'POST':
        query = request.form['query']
        results = Mantra.query.filter(
            (Mantra.title.contains(query)) | (Mantra.deity.contains(query))
        ).all()
    return render_template('mantra.html', results=results)

@app.route('/upload_aarti', methods=['GET','POST'])
def upload_aarti():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        db.session.add(Aarti(title=title,text=text))
        db.session.commit()
        return redirect('/')
    return render_template('upload_aarti.html')

@app.route('/donate', methods=['GET','POST'])
def donate():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        amount = float(request.form['amount'])
        db.session.add(Donation(name=name,email=email,amount=amount))
        db.session.commit()
        return render_template('donation_success.html', name=name, amount=amount)
    return render_template('donate.html')

# ------------------ MAIN ------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        preload_content()
    app.run(debug=True)
