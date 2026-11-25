import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from bench.report import server_itl_mean_ms


class ReportTest(unittest.TestCase):
    def test_delta_histogram(self):
        with TemporaryDirectory() as t:
            path=Path(t)/'metrics_long.csv'
            with path.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=['timestamp_utc','name','labels','value'])
                writer.writeheader()
                for ts,s,n in [('a',5.,100),('b',6.5,150)]:
                    writer.writerow({'timestamp_utc':ts,'name':'vllm:inter_token_latency_seconds_sum','value':s})
                    writer.writerow({'timestamp_utc':ts,'name':'vllm:inter_token_latency_seconds_count','value':n})
            self.assertAlmostEqual(server_itl_mean_ms(Path(t)),30)


if __name__=='__main__':
    unittest.main()
