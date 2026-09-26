import unittest
from unittest.mock import patch

try:
    import pandas as pd
except ModuleNotFoundError:  # Parser tests still run before optional runtime deps are installed.
    pd = None

from generate_spmo import _quote_from_frame, get_quotes, parse_holdings


class HoldingsTests(unittest.TestCase):
    def test_published_symbols_are_preserved_and_unquotable_rows_removed(self):
        content = b'''\xef\xbb\xbfTicker,Company,Share/ Par,% TNA,Class of shares,CUSIP,Market value
"GOOGL","Alphabet Inc Class A","1,000","35%","Common Stock","X","$35"
"GOOG","Alphabet Inc Class C","1,000","25%","ADR","X","$25"
"BRK.B","Berkshire Hathaway","1,000","20%","Real Estate Investment Trust","X","$20"
"BRK.B","Berkshire duplicate row","1,000","19.999997%","Common Stock","X","$20"
"2602335D","Unquotable","1","0.000003%","Common Stock","X","$1"
"USD","US Dollar","1","0.2%","Currency","X","$1"
# as of 2026-09-24
'''
        holdings, date, excluded = parse_holdings(content, min_holdings=3)
        self.assertEqual(date, "2026-09-24")
        self.assertEqual([(h.ticker, h.name, h.weight) for h in holdings], [
            ("BRK-B", "Berkshire duplicate row", 39.999997),
            ("GOOGL", "Alphabet Inc Class A", 35.0),
            ("GOOG", "Alphabet Inc Class C", 25.0),
        ])
        self.assertEqual([symbol for _, symbol, _ in excluded], ["2602335D"])

    def test_missing_header_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Ticker, Company and % TNA"):
            parse_holdings(b'# as of 2026-09-24\n')

    def test_missing_as_of_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "# as of"):
            parse_holdings(b'Ticker,Company,Share/ Par,% TNA,Class of shares,CUSIP,Market value\n')

    @unittest.skipIf(pd is None, "pandas is not installed")
    def test_quotes_use_previous_valid_close_and_handle_missing(self):
        days = pd.to_datetime(["2026-09-23 15:59", "2026-09-24 09:30", "2026-09-24 09:34"]).tz_localize("America/New_York")
        columns = pd.MultiIndex.from_product([["NVDA", "BRK-B"], ["Close"]])
        frame = pd.DataFrame([[120, 310], [None, 309], [117, 305]], index=days, columns=columns)
        self.assertEqual(_quote_from_frame(frame, "NVDA"), {
            "price": 117.0, "change": -3.0, "changePct": -2.5, "priceDate": "2026-09-24 06:34 PDT"
        })
        self.assertEqual(_quote_from_frame(frame, "BRK-B")["changePct"], -1.6129)
        self.assertIsNone(_quote_from_frame(frame, "MISSING"))

    @unittest.skipIf(pd is None, "pandas is not installed")
    def test_failed_quote_batch_does_not_silently_publish(self):
        with patch("yfinance.download", return_value=pd.DataFrame()):
            with self.assertRaisesRegex(RuntimeError, "existing output was kept"):
                get_quotes([f"TEST{i}" for i in range(15)],
                           batch_size=10, delay=0, retry_delay=0, max_retries=1)


if __name__ == "__main__":
    unittest.main()
