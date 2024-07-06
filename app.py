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

stats = {'win':0, 'lose':0, 'draw':0} # 통계 저장용 딕셔너리

# 데이터베이스 생성
class Score(db.Model):
    matches = db.Column(db.Integer, primary_key=True) # 게임횟수 저장용
    win = db.Column(db.Integer, nullable=False) # 승리 저장용
    lose = db.Column(db.Integer, nullable=False) # 패배 저장용
    draw = db.Column(db.Integer, nullable=False) #무승부 저장용

# 데이터베이스 삭제 함수(전적초기화 용도)
def delete_all_scores():
    try:
        # 모든 Score 레코드 삭제
        db.session.query(Score).delete()
        db.session.commit()
        print("Score 데이터 삭제 완료!")
    except Exception as e:
        db.session.rollback()
        print(f"Score 데이터 삭제 중 오류 발생: {e}")


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

    # delete_all_scores() # 데이터 베이스 초기화가 필요할때 활성화하고 다시 실행하세요.
    
    if game_result == '승리!':
        stats['win'] += 1
    elif game_result == '패배!':
        stats['lose'] += 1
    elif game_result == '무승부!':
        stats['draw'] += 1

    context = {
        'computer_pick': computer_choice,
        'your_choice': my_choice,
        'rog': game_result,
        'stats': stats
    }
    # DB 입력부분입니다.
    print(context['rog'])
    score = Score(win = stats['win'], lose = stats['lose'], draw = stats['draw'])
    
    db.session.add(score)
    
    db.session.commit()
    #여기까지 입력부분!
    return render_template('index.html', context=context)

if __name__ == '__main__':
    app.run(debug=True)