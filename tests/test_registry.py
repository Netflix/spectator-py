import builtins
import unittest

from spectator import ManualClock, Registry


class RegistryTest(unittest.TestCase):

    def test_counter(self):
        r = Registry()
        c = r.counter("test")
        self.assertEqual(c.count(), 0)
        c.increment()
        self.assertEqual(c.count(), 1)

    def test_counter_get(self):
        r = Registry()
        r.counter("test").increment()
        self.assertEqual(r.counter("test").count(), 1)

    def test_timer(self):
        r = Registry()
        t = r.timer("test")
        self.assertEqual(t.count(), 0)
        t.record(42)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_time(), 42)

    def test_timer_with(self):
        clock = ManualClock()
        r = Registry(clock)
        t = r.timer("test")
        with t.stopwatch():
            clock.set_monotonic_time(42)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_time(), 42)

    def test_iterate_empty(self):
        r = Registry()
        for m in r:
            self.fail("registry should be empty")

    def test_iterate(self):
        r = Registry()
        r.counter("counter")
        r.timer("timer")
        meters = 0
        for m in r:
            meters += 1
        self.assertEqual(2, meters)

    def test_duplicate_start(self):
        r = Registry()
        r.start()
        t1 = r._timer
        r.start()
        self.assertEqual(r._timer, t1)

    def test_publish_cleanup_noref(self):
        r = Registry()
        with r.start():
            id = r.counter('test').meterId
            r.counter('test').increment()
            self.assertTrue(id in r._meters)
            r._publish()
            self.assertFalse(id in r._meters)

    def test_publish_cleanup_ref(self):
        r = Registry()
        with r.start():
            id = r.counter('test').meterId
            c = r.counter('test')
            c.increment()
            self.assertTrue(id in r._meters)
            r._publish()
            self.assertTrue(id in r._meters)

    def test_get_measurements_only_useful(self):
        r = Registry()

        with r.start():
            # meters with reference held
            c = r.counter('counter')
            g = r.gauge('gauge')
            c.increment()
            g.set(1)
            ms = r._get_measurements()
            self.assertEqual(2, len(ms))

            # meters without reference held; only the non-nan gauge will report
            r.gauge('gauge-nan').set(float('nan'))
            r.counter('counter-zero')
            ms = r._get_measurements()
            self.assertEqual(1, len(ms))

    def test_get_measurements_gauge_not_deleted_before_ttl(self):
        clock = ManualClock()
        r = Registry(clock=clock)

        with r.start():
            r.gauge('gauge').set(1)
            ms = r._get_measurements()
            self.assertEqual(1, len(ms))

            # two cycles are required to delete a gauge after it expires
            ms = r._get_measurements()
            self.assertEqual(1, len(ms))
            ms = r._get_measurements()
            self.assertEqual(1, len(ms))

    def test_get_measurements_gauge_deleted_after_ttl(self):
        clock = ManualClock()
        r = Registry(clock=clock)

        with r.start():
            r.gauge('gauge').set(1)
            ms = r._get_measurements()
            self.assertEqual(1, len(ms))

            clock.set_wall_time(60 * 15 + 1)

            # two cycles are required to delete a gauge after it expires
            ms = r._get_measurements()
            self.assertEqual(1, len(ms))
            ms = r._get_measurements()
            self.assertEqual(0, len(ms))

    def get_entry(self, strings, payload):
        num_tags = int(payload[0])
        tags = {}
        for i in builtins.range(1, num_tags * 2, 2):
            key_idx = int(payload[i])
            val_idx = int(payload[i + 1])
            tags[strings[key_idx]] = strings[val_idx]

        op = int(payload[num_tags * 2 + 1])
        op_str = 'sum' if op == 0 else 'max'
        return (num_tags * 2 + 3, {
            'tags': tags,
            'op': op_str,
            'value': payload[num_tags * 2 + 2]
        })

    def payload_to_entries(self, payload):
        strings = []
        num_strings = payload[0]
        for i in builtins.range(num_strings):
            strings.append(payload[i + 1])

        idx = num_strings + 1
        entries = []
        while idx < len(payload):
            num_consumed, entry = self.get_entry(strings, payload[idx:])
            if num_consumed == 0:
                remaining = payload[idx:]
                self.fail("index {} - remaining {}".format(idx, remaining))
            entries.append(entry)
            idx += num_consumed

        return entries

    def test_measurements_to_json(self):
        r = Registry()
        with r.start({'common_tags': {'nf.app': 'app'}}):
            c = r.counter('c')
            c.increment()
            r.gauge('g').set(42)
            ms = r._get_measurements()

            expected_counter = {
                'op': 'sum',
                'value': 1,
                'tags': {'nf.app': 'app', 'name': 'c', 'statistic': 'count'}
            }
            expected_gauge = {
                'op': 'max',
                'value': 42,
                'tags': {'nf.app': 'app', 'name': 'g', 'statistic': 'gauge'}
            }
            expected_entries = [expected_gauge, expected_counter]

            payload = r._measurements_to_json(ms)

            # sort payload so we ensure we get gauges first
            entries = sorted(self.payload_to_entries(payload),
                             key=lambda m: m.get('op'))
            self.assertEqual(expected_entries, entries)

    def test_duplicate_gauge_different_type(self):
        r = Registry()
        c = r.counter("check_value", tags=dict(taga="a"))
        g = r.gauge("check_value", tags=dict(taga="a"))
        self.assertIsNot(c, g)
        self.assertIs(g, r.noopGauge)

    def test_duplicate_counter_different_type(self):
        r = Registry()
        g = r.gauge("check_value", tags=dict(taga="a"))
        c = r.counter("check_value", tags=dict(taga="a"))
        self.assertIsNot(g, c)
        self.assertIs(c, r.noopCounter)

    def test_duplicate_timer_different_type(self):
        r = Registry()
        c = r.counter("check_value")
        t = r.timer("check_value")
        self.assertIsNot(c, t)
        self.assertIs(t, r.noopTimer)

    def test_duplicate_distro_different_type(self):
        r = Registry()
        c = r.counter("check_value")
        d = r.distribution_summary("check_value")
        self.assertIsNot(c, d)
        self.assertIs(d, r.noopDistributionSummary)

    def test_timer_and_counter_same_name_different_tags(self):
        r = Registry()
        c = r.counter("check_value", tags=dict(tag="a"))
        t = r.timer("check_value", tags=dict(tag="b"))
        self.assertIsNot(c, t)
        self.assertIsNot(t, r.noopTimer)
