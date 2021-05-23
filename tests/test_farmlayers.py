from farmlayers.download_inputs import dates_filter
from datetime import datetime

date1 = datetime(2020, 1, 1)
date6 = datetime(2020, 6, 1)

def test_dates_filter():
    assert dates_filter(4, 8, date6)
    assert not dates_filter(4, 8, date1)
    assert dates_filter(12, 2, date1)
    assert not dates_filter(12, 2, date6)