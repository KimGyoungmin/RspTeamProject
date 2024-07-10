from flask import Flask, render_template, request, redirect, url_for
import random
import os
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
# 데이터베이스 생성코드입니다.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'Score.db')
app.config['SQLALCHEMY_BINDS'] = {
    'second_db': 'sqlite:///' + os.path.join(basedir, 'stats.db')
}
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

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


def result(my_choice, computer_choice):
    if (my_choice == '가위' and computer_choice == '보') or (my_choice == '바위' and computer_choice == '가위') or (
            my_choice == '보' and computer_choice == '바위'):
        return '승!'
    elif my_choice == computer_choice:
        return '무승부!'
    elif (my_choice == '가위' and computer_choice == '바위') or (my_choice == '바위' and computer_choice == '보') or (
            my_choice == '보' and computer_choice == '가위'):
        return '패배!'
    else:
        return '결과는?'


@app.route('/')
def home():
    score = Score.query.first()  # Score 이라는 테이블의 첫번쨰줄을 score이라는 객체생성함 실제로저장은안됨
    if score is None:  # 그  sco
        score = Score(win=0, lose=0, draw=0)
        db.session.add(score)

    if 'reset' in request.args:  # 초기화버튼이 요청으로 왔을떄
        delete_all_scores()  # 삭제요청
        return redirect(url_for('home'))

    elif 'query' in request.args:  # 입력버튼 눌렀을떄
        my_choice = request.args['query']  # 사용자값을 받아오기
        computer_choice = random.choice(['가위', '바위', '보']) # 렌덤으로 컴퓨터값 설정

        game_result = result(my_choice, computer_choice)  # 비교하는함수 result 실행

        if game_result == '승!':
            score.win += 1
        elif game_result == '패배!':
            score.lose += 1
        elif game_result == '무승부!':
            score.draw += 1
        # db.session.commit()
        stats = Stats(cpu=computer_choice, user=my_choice, result=game_result) # 한판한 결과를 stats 객체를만들어 저장
        db.session.add(stats) # 데이터베이스 add
        db.session.commit() # 데이터베이스에 진짜저장
        return redirect(url_for('home'))  # get 요청 처리 후 리디렉션


    context=Score.query.first()
    collection = Stats.query.all()
    return render_template('index.html', context=context, collection=collection)


if __name__ == '__main__':
    app.run(debug=True)
