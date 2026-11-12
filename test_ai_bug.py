import pytest

from find_max import find_max


# ---------- 정상 케이스 ----------
def test_max_in_middle():
    assert find_max([1, 5, 3]) == 5


def test_max_at_first():
    assert find_max([9, 2, 4, 1]) == 9


def test_max_at_last():
    # 마지막 원소가 최댓값인 경우 (현재 구현은 마지막 원소를 순회하지 않아 실패함)
    assert find_max([1, 2, 3, 10]) == 10


def test_unsorted_list():
    assert find_max([3, 8, 1, 7, 5]) == 8


def test_ascending_list():
    assert find_max([1, 2, 3, 4, 5]) == 5


def test_descending_list():
    assert find_max([5, 4, 3, 2, 1]) == 5


def test_float_values():
    assert find_max([1.5, 2.5, 0.5]) == 2.5


def test_mixed_int_and_float():
    assert find_max([1, 2.5, 2]) == 2.5


def test_tuple_input():
    assert find_max((4, 9, 2)) == 9


def test_does_not_modify_input():
    data = [3, 1, 2]
    find_max(data)
    assert data == [3, 1, 2]


# ---------- 경계값 ----------
def test_single_element():
    assert find_max([7]) == 7


def test_two_elements_second_larger():
    # 원소 2개: 반복 범위가 비어 두 번째 원소가 무시됨 (현재 구현은 실패)
    assert find_max([1, 5]) == 5


def test_two_elements_first_larger():
    assert find_max([5, 1]) == 5


def test_two_equal_elements():
    assert find_max([4, 4]) == 4


def test_three_elements_last_largest():
    assert find_max([1, 2, 3]) == 3


def test_all_equal_elements():
    assert find_max([2, 2, 2, 2]) == 2


def test_duplicate_max_values():
    assert find_max([1, 9, 3, 9]) == 9


def test_all_negative_numbers():
    assert find_max([-5, -2, -9]) == -2


def test_negative_and_positive():
    assert find_max([-1, 0, 1]) == 1


def test_all_zeros():
    assert find_max([0, 0, 0]) == 0


def test_zero_is_max_among_negatives():
    assert find_max([-3, -1, 0, -2]) == 0


def test_large_values():
    assert find_max([10**18, 10**19, 10**17]) == 10**19


def test_large_list_max_at_end():
    data = list(range(10_000))
    assert find_max(data) == 9_999


def test_large_list_max_at_start():
    data = list(range(10_000, 0, -1))
    assert find_max(data) == 10_000


# ---------- 예외 케이스 ----------
def test_empty_list_raises_index_error():
    with pytest.raises(IndexError):
        find_max([])


def test_empty_tuple_raises_index_error():
    with pytest.raises(IndexError):
        find_max(())


def test_none_raises_type_error():
    with pytest.raises(TypeError):
        find_max(None)


def test_non_sequence_int_raises_type_error():
    with pytest.raises(TypeError):
        find_max(123)


def test_unordered_set_raises_type_error():
    # set은 인덱싱(scores[0])을 지원하지 않음
    with pytest.raises(TypeError):
        find_max({1, 2, 3})


def test_incomparable_types_raise_type_error():
    with pytest.raises(TypeError):
        find_max([1, "a", 3])


@pytest.mark.parametrize(
    "scores, expected",
    [
        ([1], 1),
        ([1, 2], 2),
        ([2, 1], 2),
        ([1, 2, 3], 3),
        ([3, 2, 1], 3),
        ([1, 3, 2], 3),
        ([-1, -2, -3], -1),
        ([0, 0], 0),
    ],
)
def test_parametrized(scores, expected):
    assert find_max(scores) == expected
