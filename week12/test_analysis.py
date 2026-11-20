#e만
'''
아래 네 가지를 확인하는 pytest 테스트 파일을 만들어라.
파일 이름은 test_analysis.py 로 한다.

  ① scores_2026.csv 를 정제하면 100행이 남는다.
  ② 정제 후 '반' 값의 종류는 '1반'과 '2반' 두 개뿐이다.
  ③ 반으로 묶은 점수 합계의 합이 전체 점수 합계와 같다.
  ④ mini.csv 를 정제한 뒤 1반 평균이 80.0 이다.

[제약]
  - 함수 이름은 test_ 로 시작한다.
  - assert 를 쓴다.
  - 파일을 읽는 코드는 파일 맨 위에서 한 번만 실행한다.
'''



import pandas as pd

from analysis import 반별평균, 정제


df = pd.read_csv("scores_2026.csv", dtype={"학번": "string"})
df_mini = pd.read_csv("mini.csv", dtype={"학번": "string"})

def test_정제_행수():
    df_정제 = 정제(df)
    assert len(df_정제) == 100

def test_정제_반_종류():
    df_정제 = 정제(df)
    assert set(df_정제["반"].unique()) == {"1반", "2반"}

def test_정제_합계():
    df_정제 = 정제(df)
    assert df_정제.groupby("반")["점수"].sum().sum() == df_정제["점수"].sum()

def test_정제_1반_평균():
    df_정제 = 정제(df_mini)
    assert 반별평균(df_정제)["1반"] == 80.0

# test_정제_행수()
# test_정제_반_종류()
# test_정제_합계()
# test_정제_1반_평균()

'''
mini.csv 를 정제한 뒤의 1반 평균, 2반 평균을 출력하는 코드를 작성하라.
'''

df_mini_정제 = 정제(df_mini)
print(f"1반 평균: {반별평균(df_mini_정제)['1반']}")
print(f"2반 평균: {반별평균(df_mini_정제)['2반']}")


