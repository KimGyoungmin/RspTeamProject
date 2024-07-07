from flask import Flask, render_template, request
import random
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 데이터베이스 생성코드입니다.
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'Score.db')
app.config['SQLALCHEMY_BINDS'] = {
'second_db': 'sqlite:///' + os.path.join(basedir, 'stats.db')}

db = SQLAlchemy(app)

# 데이터베이스 생성
class Score(db.Model):
    matches = db.Column(db.Integer, primary_key=True) # 게임횟수 저장용
    win = db.Column(db.Integer, nullable=False) # 승리 저장용
    lose = db.Column(db.Integer, nullable=False) # 패배 저장용
    draw = db.Column(db.Integer, nullable=False) #무승부 저장용

class Stats(db.Model):
    __bind_key__ = 'second_db'
    matches = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    result = db.Column(db.String, nullable=False)

# 데이터베이스 삭제 함수(전적초기화 용도)
def delete_all_scores():
    try:
        # 모든 Score 레코드 삭제
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
    
    if my_choice is None: # 프로그램을 실행할때마다 자동으로 1회 실행되는 문제가 있어서 추가한 디버깅용 코드
        my_choice = '선택하지 않음'

    context = {
        'computer_pick': computer_choice,
        'your_choice': my_choice,
        'rog': game_result
    }
    # 출력확인용(완성판에는 삭제예정)
    print(context['rog'])
    
    # Score DB 입력(총 전적 기록)
    score = Score.query.first()
    if score is None:
        score = Score(matches=1, win=0, lose=0, draw=0)
        db.session.add(score)
        
    # Stats DB 입력(게임 결과 기록)
    score.matches += 1
    if game_result == '승!':
        score.win += 1
    elif game_result == '패배!':
        score.lose += 1
    elif game_result == '무승부!':
        score.draw += 1
    stats = Stats(cpu = computer_choice, user = my_choice, result = game_result)
    db.session.add(stats)
    
    db.session.commit()
    
    # delete_all_scores() # 데이터 베이스 초기화가 필요할때 활성화하고 게임을 1회 실행하세요.
    # ++ html의 버튼으로 해당 함수를 실행할 수 있으면 좋을것같습니다.
    
    return render_template('index.html', context=context)

if __name__ == '__main__':
    app.run(debug=True)