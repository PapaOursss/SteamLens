import unittest

from ingestion.sources.request_pacer import RequestPacer
from ingestion.tests.fakes import FakeClock


class RequestPacerTests(unittest.TestCase):
    def test_waits_only_the_remaining_time(self) -> None:
        clock = FakeClock()
        pacer = RequestPacer(60, clock=clock, sleep=clock.sleep)
        pacer.wait()
        clock.now += 15
        pacer.wait()
        self.assertEqual(clock.sleeps, [45])

    def test_no_wait_when_interval_already_elapsed(self) -> None:
        clock = FakeClock()
        pacer = RequestPacer(1, clock=clock, sleep=clock.sleep)
        pacer.wait()
        clock.now += 5
        pacer.wait()
        self.assertEqual(clock.sleeps, [])


if __name__ == "__main__":
    unittest.main()
