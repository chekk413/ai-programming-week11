from pathlib import Path

import pytest

from load_scores import load_scores

HERE = Path(__file__).parent


def 쓰기(경로, 점수):
    """점수 한 줄짜리 임시 CSV를 만든다."""
    경로.write_text(f"name,score\n테스트,{점수}\n", encoding="utf-8")


# ── 정상 ──────────────────────────────────────────────────────────────
def test_정상_파일을_읽는다():
    kept, skipped = load_scores(HERE / "scores.csv")
    assert len(kept) == 5


def test_빈_줄은_건너뛴다(tmp_path):
    파일 = tmp_path / "빈줄.csv"
    파일.write_text("name,score\n김하나,88\n\n\n이두리,70\n", encoding="utf-8")
    kept, skipped = load_scores(파일)
    assert kept == [("김하나", 88), ("이두리", 70)]
    assert skipped == []  # 빈 줄은 기록도 하지 않는다


def test_이름에_쉼표가_있어도_읽는다(tmp_path):
    파일 = tmp_path / "쉼표.csv"
    파일.write_text('name,score\n"최,네번",77\n', encoding="utf-8")
    kept, skipped = load_scores(파일)
    assert kept == [("최,네번", 77)]


# ── 예외 ──────────────────────────────────────────────────────────────
def test_없는_파일이면_오류가_난다():
    with pytest.raises(FileNotFoundError):
        load_scores("없는파일.csv")


def test_헤더만_있으면_빈_결과가_나온다():
    kept, skipped = load_scores(HERE / "empty.csv")
    assert kept == []
    assert skipped == []


# ── 커버리지(term-missing)가 알려준 안 지나간 줄을 채우는 테스트 ─────────
def test_이름이_비어_있으면_건너뛰고_기록한다():
    # 55-56번 줄 : weird.csv 2행은 ",90" — 이름만 비어 있다
    kept, skipped = load_scores(HERE / "weird.csv")
    assert (2, ",90", "이름이 비어 있음") in skipped
    assert all(name != "" for name, _ in kept)


def test_직접_실행하면_읽은_줄과_건너뛴_줄을_출력한다(monkeypatch, capsys):
    # 77-86번 줄 : python load_scores.py scores.csv
    import runpy

    monkeypatch.setattr("sys.argv", ["load_scores.py", str(HERE / "scores.csv")])
    runpy.run_path(str(HERE / "load_scores.py"), run_name="__main__")
    출력 = capsys.readouterr().out
    assert "읽은 줄 : 5개" in 출력
    assert "건너뛴 줄 : 5개" in 출력


# ── 경계값 ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("점수, 유효한가", [
    (-1,  False),   # 경계 바로 아래
    (0,   True),    # ★ 아래쪽 경계
    (1,   True),
    (99,  True),
    (100, True),    # ★ 위쪽 경계
    (101, False),   # 경계 바로 위
])
def test_점수_경계값(tmp_path, 점수, 유효한가):
    파일 = tmp_path / "임시.csv"
    쓰기(파일, 점수)
    kept, skipped = load_scores(파일)
    assert (len(kept) == 1) == 유효한가
    assert (len(skipped) == 1) == (not 유효한가)
