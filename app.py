from flask import Flask, render_template, request, redirect, url_for
import random
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 데이터베이스 생성코드입니다.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'Score.db')
app.config['SQLALCHEMY_BINDS'] = {
    'second_db': 'sqlite:///' + os.path.join(basedir, 'stats.db')
}

db = SQLAlchemy(app)

# 데이터베이스 모델 정의
class Score(db.Model):
    matches = db.Column(db.Integer, primary_key=True)
    win = db.Column(db.Integer, nullable=False)
    lose = db.Column(db.Integer, nullable=False)
    draw = db.Column(db.Integer, nullable=False)

class Stats(db.Model):
    __bind_key__ = 'second_db'
    matches = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    result = db.Column(db.String, nullable=False)

# 데이터베이스 삭제 함수
def delete_all_scores():
    try:
        db.session.query(Score).delete()
        db.session.query(Stats).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'reset' in request.form:
            delete_all_scores()
            return redirect(url_for('home'))
        elif 'query' in request.form:
            my_choice = request.form['query']
            computer_choice = random.choice(['가위', '바위', '보'])

            def result():
                if (my_choice == '가위' and computer_choice == '보') or (my_choice == '바위' and computer_choice == '가위') or (my_choice == '보' and computer_choice == '바위'):
                    return '승!'
                elif my_choice == computer_choice:
                    return '무승부!'
                elif (my_choice == '가위' and computer_choice == '바위') or (my_choice == '바위' and computer_choice == '보') or (my_choice == '보' and computer_choice == '가위'):
                    return '패배!'
                else:
                    return '결과는?'

            game_result = result()

            score = Score.query.first()
            if score is None:
                score = Score(matches=1, win=0, lose=0, draw=0)
                db.session.add(score)

            score.matches += 1
            if game_result == '승!':
                score.win += 1
            elif game_result == '패배!':
                score.lose += 1
            elif game_result == '무승부!':
                score.draw += 1

            stats = Stats(cpu=computer_choice, user=my_choice, result=game_result)
            db.session.add(stats)
            db.session.commit()

            return redirect(url_for('home'))  # POST 요청 처리 후 리디렉션

    context = {
        'computer_pick': '',
        'your_choice': '',
        'rog': '',
        'win': Score.query.first().win if Score.query.first() else 0,
        'lose': Score.query.first().lose if Score.query.first() else 0,
        'draw': Score.query.first().draw if Score.query.first() else 0,
    }

    collection = Stats.query.all()
    return render_template('index.html', context=context, collection=collection)

if __name__ == '__main__':
    app.run(debug=True)

