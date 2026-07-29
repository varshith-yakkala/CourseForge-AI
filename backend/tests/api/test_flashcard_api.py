import pytest
from datetime import datetime, timedelta, timezone

def calculate_sm2_interval(q: int, old_ease: float = 2.5, old_interval: float = 1.0, old_rep: int = 0):
    new_ease = max(1.3, old_ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    if q < 3:
        new_rep = 0
        new_interval = 1.0
    else:
        new_rep = old_rep + 1
        if new_rep == 1:
            new_interval = 1.0
        elif new_rep == 2:
            new_interval = 6.0
        else:
            new_interval = round(old_interval * new_ease, 2)
    return new_rep, new_interval, round(new_ease, 2)

def test_sm2_algorithm_easy():
    # Grade 5 (Easy) on first review
    rep, interval, ease = calculate_sm2_interval(5, 2.5, 1.0, 0)
    assert rep == 1
    assert interval == 1.0
    assert ease == 2.6

def test_sm2_algorithm_again():
    # Grade 1 (Again / Failed)
    rep, interval, ease = calculate_sm2_interval(1, 2.6, 6.0, 2)
    assert rep == 0
    assert interval == 1.0
    assert ease < 2.6
