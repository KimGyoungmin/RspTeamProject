from flask import Flask, render_template, request
import random
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# 데이터베이스 생성코드입니다.
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Score(db.Model):
    matches = db.Column(db.Integer, primary_key=True) # 게임횟수 저장용
    win = db.Column(db.Integer, nullable=False) # 승리 저장용
    lose = db.Column(db.Integer, nullable=False) # 패배 저장용
    draw = db.Column(db.Integer, nullable=False) #무승부 저장용
    
    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        my_choice = request.form['query']
    else:
        my_choice = None

    computer_choice = random.choice(['가위', '바위', '보'])

    def result():
        if (my_choice == '가위' and computer_choice == '보')or(my_choice == '바위' and computer_choice == '가위')or(my_choice == '보' and computer_choice == '바위'):
            return '승!'
        elif my_choice == computer_choice:
            return '무승부!'
        elif (my_choice == '가위' and computer_choice == '바위')or(my_choice == '바위' and computer_choice == '보')or(my_choice == '보' and computer_choice == '가위'):
            return '패배!'
        else:
            return '결과는?'
        
    game_result = result()

    context = {
        'computer_pick': computer_choice,
        'your_choice': my_choice,
        'rog': game_result
    }
    # DB 입력부분입니다.
    score = Score.query.first()
    if score:
        if result == '승리!':
            score.win += 1
        elif result == '패배!':
            score.lose += 1
        elif result == '무승부!':
            score.draw += 1
        score.matches += 1
    else:
        score = Score(matches=1, win=1 if game_result == '승!' else 0, lose=1 if game_result == '패배!' else 0, draw=1 if game_result == '무승부!' else 0)
        db.session.add(score)
    db.session.commit()
    #여기까지 입력부분!
    return render_template('index.html', context=context)

if __name__ == '__main__':
    app.run(debug=True)