# test_load_scores.py
# 가정: scores.py 의 load_scores(path) -> (rows, skipped)
#   rows    : [(이름, 점수), ...]  (점수는 숫자)
#   skipped : [(행 번호, 사유 메시지), ...]  (행 번호는 헤더를 1행으로 센 파일 기준)
#   파일/폴더 없음 -> FileNotFoundError, 헤더 없음/열 개수 불일치 -> ValueError
import pytest

from scores import load_scores


def write_csv(tmp_path, text, name="scores.csv"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def reasons(skipped):
    return " ".join(str(s[1]) for s in skipped)


def line_numbers(skipped):
    return [s[0] for s in skipped]


# ---------- 정상 ----------
def test_normal_rows(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90\nlee,75\n")
    rows, skipped = load_scores(p)
    assert [(n, float(s)) for n, s in rows] == [("kim", 90.0), ("lee", 75.0)]
    assert skipped == []


def test_accepts_str_path(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90\n")
    rows, _ = load_scores(str(p))
    assert len(rows) == 1


def test_header_only_returns_empty(tmp_path):
    p = write_csv(tmp_path, "name,score\n")
    rows, skipped = load_scores(p)
    assert rows == []
    assert skipped == []


def test_preserves_file_order(tmp_path):
    p = write_csv(tmp_path, "name,score\nc,1\na,2\nb,3\n")
    rows, _ = load_scores(p)
    assert [n for n, _ in rows] == ["c", "a", "b"]


# ---------- 경계값 ----------
@pytest.mark.parametrize("score", ["0", "100", "50"])
def test_boundary_scores_accepted(tmp_path, score):
    p = write_csv(tmp_path, f"name,score\nkim,{score}\n")
    rows, skipped = load_scores(p)
    assert len(rows) == 1
    assert float(rows[0][1]) == float(score)
    assert skipped == []


@pytest.mark.parametrize("score", ["-1", "101", "100.1", "-0.1", "1000"])
def test_out_of_range_skipped_with_message(tmp_path, score):
    p = write_csv(tmp_path, f"name,score\nkim,{score}\nlee,80\n")
    rows, skipped = load_scores(p)
    assert [n for n, _ in rows] == ["lee"]
    assert line_numbers(skipped) == [2]
    assert "0" in reasons(skipped) and "100" in reasons(skipped)


def test_no_trailing_newline(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90")
    rows, _ = load_scores(p)
    assert len(rows) == 1


# ---------- 예외: 파일 ----------
def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "nope.csv")


def test_directory_path_raises(tmp_path):
    with pytest.raises((FileNotFoundError, IsADirectoryError)):
        load_scores(tmp_path)


# ---------- 예외: 형식 ----------
def test_empty_file_raises_value_error(tmp_path):
    p = write_csv(tmp_path, "")
    with pytest.raises(ValueError):
        load_scores(p)


def test_missing_header_raises(tmp_path):
    p = write_csv(tmp_path, "kim,90\nlee,75\n")
    with pytest.raises(ValueError):
        load_scores(p)


@pytest.mark.parametrize(
    "header", ["name", "name,score,extra", "name;score"]
)
def test_wrong_header_columns_raises(tmp_path, header):
    p = write_csv(tmp_path, f"{header}\nkim,90\n")
    with pytest.raises(ValueError):
        load_scores(p)


def test_format_error_message_mentions_csv(tmp_path):
    p = write_csv(tmp_path, "name\nkim\n")
    with pytest.raises(ValueError) as exc:
        load_scores(p)
    assert "csv" in str(exc.value).lower()


# ---------- 예외: 값 ----------
def test_empty_score_skipped_with_message(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,\nlee,80\n")
    rows, skipped = load_scores(p)
    assert [n for n, _ in rows] == ["lee"]
    assert line_numbers(skipped) == [2]
    assert "비어" in reasons(skipped)


def test_whitespace_only_score_treated_as_empty(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,   \n")
    rows, skipped = load_scores(p)
    assert rows == []
    assert line_numbers(skipped) == [2]


def test_duplicate_name_excluded_and_reported(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90\nlee,70\nkim,85\n")
    rows, skipped = load_scores(p)
    assert [(n, float(s)) for n, s in rows] == [("kim", 90.0), ("lee", 70.0)]
    assert line_numbers(skipped) == [4]
    assert "두 번" in reasons(skipped) or "중복" in reasons(skipped)


def test_duplicate_three_times_reports_each_extra(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90\nkim,80\nkim,70\n")
    rows, skipped = load_scores(p)
    assert len(rows) == 1
    assert line_numbers(skipped) == [3, 4]


def test_multiple_problems_report_all_line_numbers(tmp_path):
    text = "name,score\na,50\nb,\nc,200\na,60\nd,10\n"
    p = write_csv(tmp_path, text)
    rows, skipped = load_scores(p)
    assert [n for n, _ in rows] == ["a", "d"]
    assert line_numbers(skipped) == [3, 4, 5]


def test_data_row_with_wrong_column_count_is_skipped_or_raises(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90,extra\nlee,80\n")
    try:
        rows, skipped = load_scores(p)
    except ValueError:
        return
    assert [n for n, _ in rows] == ["lee"]
    assert line_numbers(skipped) == [2]


def test_non_numeric_score_not_returned(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,abc\nlee,80\n")
    try:
        rows, skipped = load_scores(p)
    except ValueError:
        return
    assert [n for n, _ in rows] == ["lee"]
    assert line_numbers(skipped) == [2]


# ---------- 읽기 전용 ----------
def test_original_file_not_modified(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90\nkim,80\nlee,\npark,999\n")
    before_bytes = p.read_bytes()
    before_mtime = p.stat().st_mtime_ns
    load_scores(p)
    assert p.read_bytes() == before_bytes
    assert p.stat().st_mtime_ns == before_mtime


def test_no_extra_files_created(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90\n")
    before = set(tmp_path.iterdir())
    load_scores(p)
    assert set(tmp_path.iterdir()) == before


def test_read_only_file_can_be_loaded(tmp_path):
    p = write_csv(tmp_path, "name,score\nkim,90\n")
    p.chmod(0o444)
    try:
        rows, _ = load_scores(p)
        assert len(rows) == 1
    finally:
        p.chmod(0o644)
