# test_load_scores.py
import pytest

from load_scores import load_scores, MIN_SCORE, MAX_SCORE


def write_csv(tmp_path, text, name="scores.csv", encoding="utf-8"):
    """텍스트를 그대로(줄바꿈 변환 없이) 바이트로 저장하고 경로를 돌려준다."""
    p = tmp_path / name
    p.write_bytes(text.encode(encoding))
    return str(p)


HEADER = "name,score\n"


# ---------------------------------------------------------------------------
# 정상 동작
# ---------------------------------------------------------------------------
class TestNormal:
    def test_valid_rows_are_kept_in_order(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n영희,85\n민수,70\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90), ("영희", 85), ("민수", 70)]
        assert skipped == []

    def test_return_types(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n")
        kept, skipped = load_scores(path)
        assert isinstance(kept, list)
        assert isinstance(skipped, list)
        name, score = kept[0]
        assert isinstance(name, str)
        assert isinstance(score, int)

    def test_last_line_without_trailing_newline(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n영희,85")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90), ("영희", 85)]
        assert skipped == []

    def test_crlf_line_endings(self, tmp_path):
        path = write_csv(tmp_path, "name,score\r\n철수,90\r\n영희,85\r\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90), ("영희", 85)]
        assert skipped == []

    def test_utf8_bom_header_is_handled(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n", encoding="utf-8-sig")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90)]
        assert skipped == []

    def test_whitespace_around_name_and_score_is_stripped(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "  철수 ,  90  \n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90)]
        assert skipped == []

    def test_quoted_name_containing_comma_is_one_column(self, tmp_path):
        path = write_csv(tmp_path, HEADER + '"Kim, Chulsoo",88\n')
        kept, skipped = load_scores(path)
        assert kept == [("Kim, Chulsoo", 88)]
        assert skipped == []

    def test_plus_sign_score_is_accepted_as_integer(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,+75\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 75)]
        assert skipped == []

    def test_mixed_valid_and_invalid_rows(self, tmp_path):
        text = HEADER + "철수,90\n영희,abc\n민수,70\n,50\n"
        kept, skipped = load_scores(write_csv(tmp_path, text))
        assert kept == [("철수", 90), ("민수", 70)]
        assert [s[0] for s in skipped] == [3, 5]


# ---------------------------------------------------------------------------
# 예외: 파일 / 헤더
# ---------------------------------------------------------------------------
class TestFileAndHeader:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_scores(str(tmp_path / "no_such_file.csv"))

    def test_header_only_with_newline(self, tmp_path):
        path = write_csv(tmp_path, HEADER)
        assert load_scores(path) == ([], [])

    def test_header_only_without_newline(self, tmp_path):
        path = write_csv(tmp_path, "name,score")
        assert load_scores(path) == ([], [])

    def test_empty_file(self, tmp_path):
        path = write_csv(tmp_path, "")
        assert load_scores(path) == ([], [])

    def test_header_is_never_treated_as_data(self, tmp_path):
        # 헤더가 "유효한 데이터처럼" 보여도 첫 줄은 항상 건너뛴다
        path = write_csv(tmp_path, "철수,90\n영희,85\n")
        kept, skipped = load_scores(path)
        assert kept == [("영희", 85)]
        assert skipped == []


# ---------------------------------------------------------------------------
# 예외: 열 개수 (③)
# ---------------------------------------------------------------------------
class TestColumnCount:
    def test_too_many_columns_skipped(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90,extra\n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert len(skipped) == 1
        line_no, raw, reason = skipped[0]
        assert line_no == 2
        assert raw == "철수,90,extra"
        assert "열 개수" in reason

    def test_too_few_columns_skipped(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수\n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert skipped == [(2, "철수", "열 개수가 2가 아님")]

    def test_whitespace_only_line_is_one_column_and_skipped(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "   \n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert len(skipped) == 1
        assert skipped[0][0] == 2
        assert "열 개수" in skipped[0][2]

    def test_column_check_happens_before_name_check(self, tmp_path):
        # 열이 3개이면서 이름도 비어 있어도 사유는 '열 개수'
        path = write_csv(tmp_path, HEADER + ",90,x\n")
        _, skipped = load_scores(path)
        assert len(skipped) == 1
        assert "열 개수" in skipped[0][2]


# ---------------------------------------------------------------------------
# 예외: 점수 (④)
# ---------------------------------------------------------------------------
class TestScoreInvalid:
    def test_empty_score_skipped(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,\n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert skipped == [(2, "철수,", "점수가 비어 있음")]

    def test_whitespace_only_score_is_empty(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,   \n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert len(skipped) == 1
        assert "비어" in skipped[0][2]

    @pytest.mark.parametrize("bad", ["abc", "85.5", "85.0", "9e1", "N/A", "1,5", "--3", "9 0"])
    def test_non_integer_score_skipped(self, tmp_path, bad):
        # "1,5" 는 따옴표로 감싸 한 칸으로 만든다
        cell = f'"{bad}"' if "," in bad else bad
        path = write_csv(tmp_path, HEADER + f"철수,{cell}\n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert len(skipped) == 1
        assert skipped[0][0] == 2
        assert "정수가 아님" in skipped[0][2]


# ---------------------------------------------------------------------------
# 경계값 (⑤)
# ---------------------------------------------------------------------------
class TestScoreRange:
    def test_constants(self):
        assert MIN_SCORE == 0
        assert MAX_SCORE == 100

    @pytest.mark.parametrize("score", [0, 1, 50, 99, 100])
    def test_in_range_including_boundaries_kept(self, tmp_path, score):
        path = write_csv(tmp_path, HEADER + f"철수,{score}\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", score)]
        assert skipped == []

    @pytest.mark.parametrize("score", [-1, 101, -100, 1000, 999999999999])
    def test_out_of_range_skipped(self, tmp_path, score):
        path = write_csv(tmp_path, HEADER + f"철수,{score}\n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert skipped == [(2, f"철수,{score}", "점수가 0~100 밖")]

    def test_negative_zero_is_zero_and_kept(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,-0\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 0)]
        assert skipped == []

    def test_leading_zeros_are_accepted(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,007\n")
        kept, _ = load_scores(path)
        assert kept == [("철수", 7)]


# ---------------------------------------------------------------------------
# 예외: 이름 (⑥)
# ---------------------------------------------------------------------------
class TestNameInvalid:
    def test_empty_name_skipped(self, tmp_path):
        path = write_csv(tmp_path, HEADER + ",90\n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert skipped == [(2, ",90", "이름이 비어 있음")]

    def test_whitespace_only_name_skipped(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "   ,90\n")
        kept, skipped = load_scores(path)
        assert kept == []
        assert len(skipped) == 1
        assert "이름이 비어" in skipped[0][2]

    def test_empty_name_and_empty_score_reports_name(self, tmp_path):
        path = write_csv(tmp_path, HEADER + ",\n")
        _, skipped = load_scores(path)
        assert len(skipped) == 1
        assert "이름이 비어" in skipped[0][2]

    def test_empty_name_and_invalid_score_reports_name(self, tmp_path):
        path = write_csv(tmp_path, HEADER + ",abc\n")
        _, skipped = load_scores(path)
        assert len(skipped) == 1
        assert "이름이 비어" in skipped[0][2]

    def test_empty_name_and_out_of_range_score_reports_name(self, tmp_path):
        path = write_csv(tmp_path, HEADER + ",500\n")
        _, skipped = load_scores(path)
        assert len(skipped) == 1
        assert "이름이 비어" in skipped[0][2]


# ---------------------------------------------------------------------------
# 중복 이름: 지우지 않고 둘 다 남긴다 (v5)
# ---------------------------------------------------------------------------
class TestDuplicateNames:
    def test_duplicate_names_both_kept(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n철수,70\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90), ("철수", 70)]
        assert skipped == []

    def test_duplicate_with_same_score_both_kept(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n철수,90\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90), ("철수", 90)]
        assert skipped == []

    def test_duplicate_name_differing_only_by_whitespace_both_kept(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n 철수 ,80\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90), ("철수", 80)]
        assert skipped == []

    def test_duplicate_where_one_is_invalid_keeps_only_valid(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,90\n철수,abc\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90)]
        assert len(skipped) == 1
        assert skipped[0][0] == 3


# ---------------------------------------------------------------------------
# 빈 줄
# ---------------------------------------------------------------------------
class TestBlankLines:
    def test_blank_lines_skipped_without_record(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "\n철수,90\n\n\n영희,85\n\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90), ("영희", 85)]
        assert skipped == []

    def test_header_followed_only_by_blank_lines(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "\n\n\n")
        assert load_scores(path) == ([], [])

    def test_blank_lines_still_count_toward_line_numbers(self, tmp_path):
        # 1:헤더  2:빈 줄  3:철수,90  4:빈 줄  5:영희,abc
        path = write_csv(tmp_path, HEADER + "\n철수,90\n\n영희,abc\n")
        kept, skipped = load_scores(path)
        assert kept == [("철수", 90)]
        assert skipped == [(5, "영희,abc", "점수가 정수가 아님")]


# ---------------------------------------------------------------------------
# 건너뛴 줄 기록 형식
# ---------------------------------------------------------------------------
class TestSkippedRecordFormat:
    def test_skipped_tuple_shape(self, tmp_path):
        path = write_csv(tmp_path, HEADER + "철수,abc\n")
        _, skipped = load_scores(path)
        assert len(skipped) == 1
        line_no, raw, reason = skipped[0]
        assert isinstance(line_no, int)
        assert isinstance(raw, str)
        assert isinstance(reason, str) and reason != ""

    def test_line_numbers_are_one_based_file_lines(self, tmp_path):
        text = HEADER + "철수,90\n영희,abc\n민수,101\n,70\n하나,1,2\n"
        _, skipped = load_scores(write_csv(tmp_path, text))
        assert [s[0] for s in skipped] == [3, 4, 5, 6]

    def test_raw_line_is_preserved_with_original_spacing(self, tmp_path):
        path = write_csv(tmp_path, HEADER + " 철수 , abc \n")
        _, skipped = load_scores(path)
        assert skipped[0][1] == " 철수 , abc "

    def test_skipped_in_file_order(self, tmp_path):
        text = HEADER + "a,x\nb,200\n,3\nc\n"
        _, skipped = load_scores(write_csv(tmp_path, text))
        line_nos = [s[0] for s in skipped]
        assert line_nos == sorted(line_nos)
        assert len(skipped) == 4

    def test_every_data_line_is_either_kept_or_skipped(self, tmp_path):
        text = HEADER + "a,1\nb,x\nc,100\nd,101\ne,5,6\n,9\nf,0\n"
        kept, skipped = load_scores(write_csv(tmp_path, text))
        assert len(kept) + len(skipped) == 7
        assert [k[0] for k in kept] == ["a", "c", "f"]
