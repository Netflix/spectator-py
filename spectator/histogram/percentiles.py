from ..timer import StopWatch


class PercentileBuckets:

    def __init__(self):
        pass

    @staticmethod
    def get(i):
        return PercentileBuckets._bucket_values[i]

    @staticmethod
    def length():
        return len(PercentileBuckets._bucket_values)

    @staticmethod
    def _num_leading_zeros(v):
        leading = 64
        while v > 0:
            v >>= 1
            leading -= 1
        return leading

    @staticmethod
    def index_of(v):
        if v <= 0:
            return 0
        elif v <= 4:
            return v
        else:
            lz = PercentileBuckets._num_leading_zeros(v)
            shift = 64 - lz - 1
            prevPowerOf2 = (v >> shift) << shift
            prevPowerOf4 = prevPowerOf2
            if shift % 2 != 0:
                shift -= 1
                prevPowerOf4 = prevPowerOf2 >> 1

            base = prevPowerOf4
            delta = int(base / 3)
            offset = int((v - base) / delta)
            pos = offset + PercentileBuckets._power_of_4_index[int(shift / 2)]
            if pos >= PercentileBuckets.length() - 1:
                return PercentileBuckets.length() - 1
            else:
                return pos + 1

    @staticmethod
    def bucket(v):
        return PercentileBuckets._bucket_values[PercentileBuckets.index_of(v)]

    @staticmethod
    def _check_arg(condition, message):
        if not condition:
            raise AssertionError(message)

    @staticmethod
    def percentiles(counts, pcts, results):
        PercentileBuckets._check_arg(
            len(counts) == PercentileBuckets.length(),
            "counts is not the same size as buckets array")
        PercentileBuckets._check_arg(
            len(pcts) > 0,
            "pct array cannot be empty")
        PercentileBuckets._check_arg(
            len(pcts) == len(results),
            "pcts is not the same size as results array")

        total = 0
        for c in counts:
            total += c

        pctIdx = 0

        prev = 0
        prevP = 0.0
        prevB = 0
        for i in range(PercentileBuckets.length()):
            next = prev + counts[i]
            nextP = 100.0 * next / total
            nextB = PercentileBuckets._bucket_values[i]
            while pctIdx < len(pcts) and nextP >= pcts[pctIdx]:
                f = (pcts[pctIdx] - prevP) / (nextP - prevP)
                results[pctIdx] = f * (nextB - prevB) + prevB
                pctIdx += 1
            if pctIdx >= len(pcts):
                break
            prev = next
            prevP = nextP
            prevB = nextB

        nextP = 100.0
        nextB = PercentileBuckets._max_value
        while pctIdx < len(pcts):
            f = (pcts[pctIdx] - prevP) / (nextP - prevP)
            results[pctIdx] = f * (nextB - prevB) + prevB
            pctIdx += 1

    @staticmethod
    def percentile(counts, p):
        pcts = [p]
        results = [0.0]
        PercentileBuckets.percentiles(counts, pcts, results)
        return results[0]

    _max_value = 9223372036854775807

    _bucket_values = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        16,
        21,
        26,
        31,
        36,
        41,
        46,
        51,
        56,
        64,
        85,
        106,
        127,
        148,
        169,
        190,
        211,
        232,
        256,
        341,
        426,
        511,
        596,
        681,
        766,
        851,
        936,
        1024,
        1365,
        1706,
        2047,
        2388,
        2729,
        3070,
        3411,
        3752,
        4096,
        5461,
        6826,
        8191,
        9556,
        10921,
        12286,
        13651,
        15016,
        16384,
        21845,
        27306,
        32767,
        38228,
        43689,
        49150,
        54611,
        60072,
        65536,
        87381,
        109226,
        131071,
        152916,
        174761,
        196606,
        218451,
        240296,
        262144,
        349525,
        436906,
        524287,
        611668,
        699049,
        786430,
        873811,
        961192,
        1048576,
        1398101,
        1747626,
        2097151,
        2446676,
        2796201,
        3145726,
        3495251,
        3844776,
        4194304,
        5592405,
        6990506,
        8388607,
        9786708,
        11184809,
        12582910,
        13981011,
        15379112,
        16777216,
        22369621,
        27962026,
        33554431,
        39146836,
        44739241,
        50331646,
        55924051,
        61516456,
        67108864,
        89478485,
        111848106,
        134217727,
        156587348,
        178956969,
        201326590,
        223696211,
        246065832,
        268435456,
        357913941,
        447392426,
        536870911,
        626349396,
        715827881,
        805306366,
        894784851,
        984263336,
        1073741824,
        1431655765,
        1789569706,
        2147483647,
        2505397588,
        2863311529,
        3221225470,
        3579139411,
        3937053352,
        4294967296,
        5726623061,
        7158278826,
        8589934591,
        10021590356,
        11453246121,
        12884901886,
        14316557651,
        15748213416,
        17179869184,
        22906492245,
        28633115306,
        34359738367,
        40086361428,
        45812984489,
        51539607550,
        57266230611,
        62992853672,
        68719476736,
        91625968981,
        114532461226,
        137438953471,
        160345445716,
        183251937961,
        206158430206,
        229064922451,
        251971414696,
        274877906944,
        366503875925,
        458129844906,
        549755813887,
        641381782868,
        733007751849,
        824633720830,
        916259689811,
        1007885658792,
        1099511627776,
        1466015503701,
        1832519379626,
        2199023255551,
        2565527131476,
        2932031007401,
        3298534883326,
        3665038759251,
        4031542635176,
        4398046511104,
        5864062014805,
        7330077518506,
        8796093022207,
        10262108525908,
        11728124029609,
        13194139533310,
        14660155037011,
        16126170540712,
        17592186044416,
        23456248059221,
        29320310074026,
        35184372088831,
        41048434103636,
        46912496118441,
        52776558133246,
        58640620148051,
        64504682162856,
        70368744177664,
        93824992236885,
        117281240296106,
        140737488355327,
        164193736414548,
        187649984473769,
        211106232532990,
        234562480592211,
        258018728651432,
        281474976710656,
        375299968947541,
        469124961184426,
        562949953421311,
        656774945658196,
        750599937895081,
        844424930131966,
        938249922368851,
        1032074914605736,
        1125899906842624,
        1501199875790165,
        1876499844737706,
        2251799813685247,
        2627099782632788,
        3002399751580329,
        3377699720527870,
        3752999689475411,
        4128299658422952,
        4503599627370496,
        6004799503160661,
        7505999378950826,
        9007199254740991,
        10508399130531156,
        12009599006321321,
        13510798882111486,
        15011998757901651,
        16513198633691816,
        18014398509481984,
        24019198012642645,
        30023997515803306,
        36028797018963967,
        42033596522124628,
        48038396025285289,
        54043195528445950,
        60047995031606611,
        66052794534767272,
        72057594037927936,
        96076792050570581,
        120095990063213226,
        144115188075855871,
        168134386088498516,
        192153584101141161,
        216172782113783806,
        240191980126426451,
        264211178139069096,
        288230376151711744,
        384307168202282325,
        480383960252852906,
        576460752303423487,
        672537544353994068,
        768614336404564649,
        864691128455135230,
        960767920505705811,
        1056844712556276392,
        1152921504606846976,
        1537228672809129301,
        1921535841011411626,
        2305843009213693951,
        2690150177415976276,
        3074457345618258601,
        3458764513820540926,
        3843071682022823251,
        4227378850225105576,
        9223372036854775807
    ]

    _power_of_4_index = [
        0,
        3,
        14,
        23,
        32,
        41,
        50,
        59,
        68,
        77,
        86,
        95,
        104,
        113,
        122,
        131,
        140,
        149,
        158,
        167,
        176,
        185,
        194,
        203,
        212,
        221,
        230,
        239,
        248,
        257,
        266,
        275
    ]


class PercentileTimer:

    def __init__(self, registry, name, tags=None, min=10e-3, max=60):
        self._registry = registry
        self._name = name
        if tags is None:
            self._tags = {}
        else:
            self._tags = tags
        self._min = min * 1e9
        self._max = max * 1e9
        self._clock = registry.clock()
        self._timer = self._registry.timer(self._name, self._tags)

        # Lazily populated when percentile() is called
        self._counters = None

    def _counter_for(self, i):
        p = PercentileTimer._tag_values[i]
        tags = self._tags.copy()
        tags['statistic'] = 'percentile'
        tags['percentile'] = p
        return self._registry.counter(self._name, tags)

    def _restrict(self, amount):
        v = amount * 1e9
        v = min(v, self._max)
        v = max(v, self._min)
        return int(v)

    def record(self, amount):
        self._timer.record(amount)
        nanos = self._restrict(amount)
        self._counter_for(PercentileBuckets.index_of(nanos)).increment()

    def stopwatch(self):
        return StopWatch(self)

    def count(self):
        return self._timer.count()

    def total_time(self):
        return self._timer.total_time()

    def percentile(self, p):
        if self._counters is None:
            self._counters = [
                self._counter_for(i) for i in range(PercentileBuckets.length())
            ]

        counts = [c.count() for c in self._counters]
        v = PercentileBuckets.percentile(counts, p)
        return v / 1e9

    # Precomputed values for the corresponding buckets
    _tag_values = [
        "T{:04X}".format(i) for i in range(PercentileBuckets.length())
    ]


class PercentileDistributionSummary:

    def __init__(
            self,
            registry,
            name,
            tags=None,
            min=0,
            max=PercentileBuckets._max_value):
        self._registry = registry
        self._name = name
        if tags is None:
            self._tags = {}
        else:
            self._tags = tags
        self._min = min
        self._max = max
        self._summary = self._registry.distribution_summary(
            self._name,
            self._tags)
        self._counters = [
            self._counter_for(i) for i in range(PercentileBuckets.length())
        ]

    def _counter_for(self, i):
        p = PercentileDistributionSummary._tag_values[i]
        tags = self._tags.copy()
        tags['statistic'] = 'percentile'
        tags['percentile'] = p
        return self._registry.counter(self._name, tags)

    def _restrict(self, amount):
        v = amount
        v = min(v, self._max)
        v = max(v, self._min)
        return int(v)

    def record(self, amount):
        self._summary.record(amount)
        restricted = self._restrict(amount)
        self._counters[PercentileBuckets.index_of(restricted)].increment()

    def count(self):
        return self._summary.count()

    def total_amount(self):
        return self._summary.total_amount()

    def percentile(self, p):
        counts = [c.count() for c in self._counters]
        return PercentileBuckets.percentile(counts, p)

    # Precomputed values for the corresponding buckets
    _tag_values = [
        "D{:04X}".format(i) for i in range(PercentileBuckets.length())
    ]
