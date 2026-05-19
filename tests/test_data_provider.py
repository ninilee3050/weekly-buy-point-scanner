from __future__ import annotations

import pandas as pd

from data_provider import _chart_payload_to_dataframe, _drop_incomplete_current_week


def test_chart_payload_to_dataframe_normalizes_yahoo_weekly_rows() -> None:
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1704412800, 1705017600],
                    "indicators": {
                        "quote": [
                            {
                                "open": [100.0, 101.0],
                                "high": [105.0, 106.0],
                                "low": [99.0, 100.0],
                                "close": [104.0, 105.0],
                                "volume": [1000, 1100],
                            }
                        ],
                        "adjclose": [{"adjclose": [104.0, 105.0]}],
                    },
                }
            ],
            "error": None,
        }
    }

    result = _chart_payload_to_dataframe(payload)

    assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume", "Adj Close"]
    assert isinstance(result.index, pd.DatetimeIndex)
    assert result.iloc[0]["Open"] == 100.0
    assert result.iloc[1]["Close"] == 105.0


def test_drop_incomplete_current_week_removes_all_rows_in_current_week(monkeypatch) -> None:
    class FixedTimestamp(pd.Timestamp):
        @classmethod
        def today(cls, tz=None):
            return cls("2026-05-20")

    monkeypatch.setattr(pd, "Timestamp", FixedTimestamp)
    data = pd.DataFrame(
        {"Close": [1.0, 2.0, 3.0, 4.0]},
        index=pd.to_datetime(["2026-05-08", "2026-05-15", "2026-05-18", "2026-05-19"]),
    )

    result = _drop_incomplete_current_week(data)

    assert result.index.strftime("%Y-%m-%d").tolist() == ["2026-05-08", "2026-05-15"]
