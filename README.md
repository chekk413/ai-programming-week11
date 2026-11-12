# 성적 CSV 읽기 (`load_scores`) + 테스트

## 무엇을 하나요 (What)

성적 CSV 파일을 읽어 **유효한 (이름, 점수) 목록**과 **건너뛴 줄의 기록**을 함께 돌려주는 파이썬 함수 `load_scores(path)` 와, 이 함수를 시험하는 pytest 테스트 모음입니다.

## 왜 만들었나요 (Why)

실제 성적 파일에는 점수 칸이 빈 줄, 105점이나 -5점 같은 범위 밖 점수, "결석" 같은 글자, 열이 3개인 줄, 이름에 쉼표가 든 줄이 섞여 있습니다(`scores.csv`, `weird.csv`). 그냥 읽으면 프로그램이 죽거나, 오류 없이 틀린 점수가 평균에 들어갑니다.

그래서 이 함수는 문제 있는 줄을 **몇 행인지와 이유**를 적어 건너뛰고, 정상 줄만 돌려줍니다. 테스트는 "이 함수가 정말 그렇게 동작하는지"를 사람이 다시 확인하지 않아도 되게 하려고 만들었습니다. (12주차에 이 위에 데이터 분석 코드를 얹을 때, 분석 결과가 맞는지 검증하는 도구로 씁니다.)

## 어떻게 쓰나요 (How)

```bash
git clone https://github.com/chekk413/ai-programming-week11.git
cd ai-programming-week11
pip install pytest pytest-cov

python load_scores.py scores.csv      # 읽은 줄과 건너뛴 줄을 화면에 출력
```

Python 3.14 에서 확인했습니다. 실행 결과(앞부분):

```
읽은 줄 : 5개
  김하나 88
  최,네번 77
  김하나 91
  윤보람 64
  서한별 95
건너뛴 줄 : 5개
  3행  이두리,105   ← 점수가 0~100 밖
  4행  박세찬,   ← 점수가 비어 있음
  ...
```

코드에서 쓸 때는 다음과 같습니다.

```python
from load_scores import load_scores
kept, skipped = load_scores("scores.csv")   # kept: [(이름, 점수)], skipped: [(줄번호, 원본줄, 이유)]
```

## 어떻게 테스트하나요

```bash
pytest                                                    # 내 테스트 + AI(A) 테스트
pytest --cov=load_scores --cov-report=term-missing        # 커버리지(안 지나간 줄 보기)
```

통과 화면:

```
collected 71 items

test_ai_A.py ..........................................................  [ 81%]
test_load_scores.py .............                                        [100%]

============================= 71 passed in 0.48s ==============================
```

`pytest test_load_scores.py --cov=load_scores --cov-report=term-missing` 의 결과는 13개 통과, 커버리지 100% 입니다.

`test_ai_B.py` 와 `test_ai_bug.py` 는 AI가 쓴 원문을 **고치지 않고** 보관한 것이라 일부러 `pytest` 기본 실행에서 뺐습니다. AI가 모듈 이름을 `scores`, `find_max` 로 추측해서 그대로는 `ModuleNotFoundError` 로 멈춥니다. 확인하려면 파일 이름을 직접 적어 실행하세요.

```bash
pytest test_ai_B.py
pytest test_ai_bug.py
```

## 파일 구성

| 파일 | 하는 일 |
|---|---|
| `load_scores.py` | 성적 CSV를 읽는 함수 (배포 버전, 10주차 v5 정리본) |
| `scores.csv` · `empty.csv` · `weird.csv` | 예제 입력. 정상+문제 줄 섞임 / 헤더만 / 이상한 값 모음 |
| `test_load_scores.py` | **내가 설계해서 만든 테스트** (정상·예외·경계값 + 안 지나간 줄 채우기) |
| `test_ai_A.py` | AI에게 **코드를 줘서** 받은 테스트 (원문 그대로) |
| `test_ai_B.py` | AI에게 **명세만 줘서** 받은 테스트 (원문 그대로) |
| `test_ai_bug.py` | AI에게 **고장난 코드(`bug3_logic.py`)를 줘서** 받은 테스트 (원문 그대로) |
| `bug3_logic.py` | 8주차 함정 실험용 파일 (`find_max` 가 마지막 원소를 안 봄) |
| `prompts.txt` | A / B / 함정 프롬프트 원문 |
| `pytest.ini` | `pytest` 기본 실행 대상 설정 |
| `LICENSE` · `.gitignore` | MIT 라이선스, 파이썬 무시 목록 |

## 만든 사람 · AI를 어디에 썼는지

- 만든 사람: 민정인 (학번 2026100023), 한국기술교육대학교, AI 협업 프로그래밍 11주차 실습
- `load_scores.py`, 예제 CSV, `bug3_logic.py`, `prompts.txt` 는 수업에서 배포한 파일입니다.
- 테스트 설계표(어떤 케이스를 만들지)는 코드를 보기 전에 10주차 명세서만 보고 정했습니다.
- `test_load_scores.py` 와 이 README 는 Claude Code(claude-sonnet-5-5)의 도움을 받아 작성했습니다.
- `test_ai_A.py` · `test_ai_B.py` · `test_ai_bug.py` 는 같은 모델(Claude Sonnet 5.5)을 새 대화에서 세 번 따로 불러 받은 출력을 그대로 저장한 것입니다.
