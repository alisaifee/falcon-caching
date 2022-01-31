import sys
import random
import time
import pytest
from falcon_caching import Cache
from falcon_caching.cache import function_namespace

from tests.conftest import EVICTION_STRATEGIES


def test_memoize(caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize(3)
    def big_foo(a, b):
        return a + b + random.randrange(0, 100000)

    result = big_foo(5, 2)

    time.sleep(1)

    assert big_foo(5, 2) == result

    result2 = big_foo(5, 3)
    assert result2 != result

    time.sleep(3)

    assert big_foo(5, 2) != result

    time.sleep(1)

    assert big_foo(5, 3) != result2


def test_memoize_hashes(caches, hash_method):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize(3, hash_method=hash_method)
    def big_foo(a, b):
        return a + b + random.randrange(0, 100000)

    result = big_foo(5, 2)

    time.sleep(1)

    assert big_foo(5, 2) == result

    result2 = big_foo(5, 3)
    assert result2 != result

    time.sleep(3)

    assert big_foo(5, 2) != result

    time.sleep(1)

    assert big_foo(5, 3) != result2


def test_memoize_timeout(caches, app):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    cache.cache_options["default_timeout"] = 1

    @cache.memoize()
    def big_foo(a, b):
        return a + b + random.randrange(0, 100000)

    result = big_foo(5, 2)
    assert big_foo(5, 2) == result
    time.sleep(2)
    assert big_foo(5, 2) != result


def test_memoize_annotated(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    if sys.version_info >= (3, 0):
        @cache.memoize(50)
        def big_foo_annotated(a, b):
            return a + b + random.randrange(0, 100000)
        big_foo_annotated.__annotations__ = {'a': int, 'b': int, 'return': int}

        result = big_foo_annotated(5, 2)

        time.sleep(1)

        assert big_foo_annotated(5, 2) == result


def test_memoize_utf8_arguments(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b):
        return "{}-{}".format(a, b)

    big_foo("æøå", "chars")


def test_memoize_unicode_arguments(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b):
        return u"{}-{}".format(a, b)

    big_foo(u"æøå", "chars")


def test_memoize_delete(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize(5)
    def big_foo(a, b):
        return a + b + random.randrange(0, 100000)

    result = big_foo(5, 2)
    result2 = big_foo(5, 3)

    time.sleep(1)

    assert big_foo(5, 2) == result
    assert big_foo(5, 2) == result
    assert big_foo(5, 3) != result
    assert big_foo(5, 3) == result2

    cache.delete_memoized(big_foo)

    assert big_foo(5, 2) != result
    assert big_foo(5, 3) != result2


def test_memoize_no_timeout_delete(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b):
        return a + b + random.randrange(0, 100000)

    result_a = big_foo(5, 1)
    result_b = big_foo(5, 2)

    assert big_foo(5, 1) == result_a
    assert big_foo(5, 2) == result_b
    cache.delete_memoized(big_foo, 5, 2)

    assert big_foo(5, 1) == result_a
    assert big_foo(5, 2) != result_b

    # Cleanup bigfoo 5,1 5,2 or it might conflict with
    # following run if it also uses memecache
    cache.delete_memoized(big_foo, 5, 2)
    cache.delete_memoized(big_foo, 5, 1)


def test_memoize_verhash_delete(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize(5)
    def big_foo(a, b):
        return a + b + random.randrange(0, 100000)

    result = big_foo(5, 2)
    result2 = big_foo(5, 3)

    time.sleep(1)

    assert big_foo(5, 2) == result
    assert big_foo(5, 2) == result
    assert big_foo(5, 3) != result
    assert big_foo(5, 3) == result2

    cache.delete_memoized_verhash(big_foo)

    _fname, _fname_instance = function_namespace(big_foo)
    version_key = cache._memvname(_fname)
    assert cache.get(version_key) is None

    assert big_foo(5, 2) != result
    assert big_foo(5, 3) != result2

    assert cache.get(version_key) is not None


def test_memoize_annotated_delete(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize(5)
    def big_foo_annotated(a, b):
        return a + b + random.randrange(0, 100000)

    big_foo_annotated.__annotations__ = {'a': int, 'b': int, 'return': int}

    result = big_foo_annotated(5, 2)
    result2 = big_foo_annotated(5, 3)

    time.sleep(1)

    assert big_foo_annotated(5, 2) == result
    assert big_foo_annotated(5, 2) == result
    assert big_foo_annotated(5, 3) != result
    assert big_foo_annotated(5, 3) == result2

    cache.delete_memoized_verhash(big_foo_annotated)

    _fname, _fname_instance = function_namespace(big_foo_annotated)
    version_key = cache._memvname(_fname)
    assert cache.get(version_key) is None

    assert big_foo_annotated(5, 2) != result
    assert big_foo_annotated(5, 3) != result2

    assert cache.get(version_key) is not None


def test_memoize_args(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b):
        return sum(a) + sum(b) + random.randrange(0, 100000)

    result_a = big_foo([5, 3, 2], [1])
    result_b = big_foo([3, 3], [3, 1])

    assert big_foo([5, 3, 2], [1]) == result_a
    assert big_foo([3, 3], [3, 1]) == result_b

    cache.delete_memoized(big_foo, [5, 3, 2], [1])

    assert big_foo([5, 3, 2], [1]) != result_a
    assert big_foo([3, 3], [3, 1]) == result_b

    # Cleanup bigfoo 5,1 5,2 or it might conflict with
    # following run if it also uses memecache
    cache.delete_memoized(big_foo, [5, 3, 2], [1])
    cache.delete_memoized(big_foo, [3, 3], [1])


def test_memoize_kwargs(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b=None):
        return a + sum(b.values()) + random.randrange(0, 100000)

    result_a = big_foo(1, dict(one=1, two=2))
    result_b = big_foo(5, dict(three=3, four=4))

    assert big_foo(1, dict(one=1, two=2)) == result_a
    assert big_foo(5, dict(three=3, four=4)) == result_b

    cache.delete_memoized(big_foo, 1, dict(one=1, two=2))

    assert big_foo(1, dict(one=1, two=2)) != result_a
    assert big_foo(5, dict(three=3, four=4)) == result_b


def test_memoize_kwargonly(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a=None):
        if a is None:
            a = 0
        return a + random.random()

    result_a = big_foo()
    result_b = big_foo(5)

    assert big_foo() == result_a
    assert big_foo() < 1
    assert big_foo(5) == result_b
    assert big_foo(5) >= 5 and big_foo(5) < 6


def test_memoize_arg_kwarg(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def f(a, b, c=1):
        return a + b + c + random.randrange(0, 100000)

    assert f(1, 2) == f(1, 2, c=1)
    assert f(1, 2) == f(1, 2, 1)
    assert f(1, 2) == f(1, 2)
    assert f(1, 2, 3) != f(1, 2)

    with pytest.raises(TypeError):
        f(1)


def test_memoize_arg_kwarg_var_keyword(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def f(a, b, c=1, **kwargs):
        return a + b + c + random.randrange(0, 100000) + sum(list(kwargs.values()))

    assert f(1, 2) == f(1, 2, c=1)
    assert f(1, 2) == f(1, 2, 1)
    assert f(1, 2) == f(1, 2)
    assert f(1, 2, d=5, e=8) == f(1, 2, e=8, d=5)
    assert f(1, b=2, c=3, d=5, e=8) == f(1, 2, e=8, d=5, b=2, c=3)
    assert f(1, 2, 3) != f(1, 2)
    assert f(1, 2, 3) != f(1, 2)

    with pytest.raises(TypeError):
        f(1)


def test_memoize_classarg(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def bar(a):
        return a.value + random.random()

    class Adder(object):
        def __init__(self, value):
            self.value = value

    adder = Adder(15)
    adder2 = Adder(20)

    y = bar(adder)
    z = bar(adder2)

    assert y != z
    assert bar(adder) == y
    assert bar(adder) != z
    adder.value = 14
    assert bar(adder) == y
    assert bar(adder) != z

    assert bar(adder) != bar(adder2)
    assert bar(adder2) == z


def test_memoize_classfunc(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    class Adder(object):
        def __init__(self, initial):
            self.initial = initial

        @cache.memoize()
        def add(self, b):
            return self.initial + b

    adder1 = Adder(1)
    adder2 = Adder(2)

    x = adder1.add(3)
    assert adder1.add(3) == x
    assert adder1.add(4) != x
    assert adder1.add(3) != adder2.add(3)


def test_memoize_classfunc_repr(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    class Adder(object):
        def __init__(self, initial):
            self.initial = initial

        @cache.memoize()
        def add(self, b):
            return self.initial + b

        def __repr__(self):
            return "42"

        def __caching_id__(self):
            return self.initial

    adder1 = Adder(1)
    adder2 = Adder(2)

    x = adder1.add(3)
    assert adder1.add(3) == x
    assert adder1.add(4) != x
    assert adder1.add(3) != adder2.add(3)


def test_memoize_classfunc_delete(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    # skip the test for filesystem as there is no delete there
    if cache.config['CACHE_TYPE'] in ['filesystem']:
        return

    class Adder(object):
        def __init__(self, initial):
            self.initial = initial

        @cache.memoize()
        def add(self, b):
            return self.initial + b + random.random()

    adder1 = Adder(1)
    adder2 = Adder(2)

    a1 = adder1.add(3)
    a2 = adder2.add(3)

    assert a1 != a2
    assert adder1.add(3) == a1
    assert adder2.add(3) == a2

    cache.delete_memoized(adder1.add)

    a3 = adder1.add(3)
    a4 = adder2.add(3)

    assert not a1 == a3
    # self.assertNotEqual(a1, a3)

    assert a1 != a3

    assert a2 == a4
    # self.assertEqual(a2, a4)

    cache.delete_memoized(Adder.add)

    a5 = adder1.add(3)
    a6 = adder2.add(3)

    assert not a5 == a6
    assert not a3 == a5
    assert not a4 == a6


def test_memoize_classmethod_delete(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    class Mock(object):
        @classmethod
        @cache.memoize(5)
        def big_foo(cls, a, b):
            return a + b + random.randrange(0, 100000)

    result = Mock.big_foo(5, 2)
    result2 = Mock.big_foo(5, 3)

    time.sleep(1)

    assert Mock.big_foo(5, 2) == result
    assert Mock.big_foo(5, 2) == result
    assert Mock.big_foo(5, 3) != result
    assert Mock.big_foo(5, 3) == result2

    cache.delete_memoized(Mock.big_foo)

    assert Mock.big_foo(5, 2) != result
    assert Mock.big_foo(5, 3) != result2


def test_memoize_classmethod_delete_with_args(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return
    if cache.config['CACHE_TYPE'] in ['redis']:
        return

    class Mock(object):
        @classmethod
        @cache.memoize(5)
        def big_foo(cls, a, b):
            return a + b + random.randrange(0, 100000)

    result = Mock.big_foo(5, 2)
    result2 = Mock.big_foo(5, 3)

    time.sleep(1)

    assert Mock.big_foo(5, 2) == result
    assert Mock.big_foo(5, 2) == result
    assert Mock.big_foo(5, 3) != result
    assert Mock.big_foo(5, 3) == result2

    with pytest.raises(ValueError):
        cache.delete_memoized(Mock.big_foo, 5, 2)

    assert Mock.big_foo(5, 2) == result
    assert Mock.big_foo(5, 3) == result2

    cache.delete_memoized(Mock.big_foo, Mock, 5, 2)

    assert Mock.big_foo(5, 2) != result
    assert Mock.big_foo(5, 3) == result2


def test_memoize_forced_update(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    forced_update = False

    @cache.memoize(5, forced_update=lambda: forced_update)
    def big_foo(a, b):
        return a + b + random.randrange(0, 100000)

    result = big_foo(5, 2)
    time.sleep(1)
    assert big_foo(5, 2) == result

    forced_update = True
    new_result = big_foo(5, 2)
    assert new_result != result

    forced_update = False
    time.sleep(1)
    assert big_foo(5, 2) == new_result


def test_memoize_forced_update_parameters(app, caches):
    from collections import Counter

    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    call_counter = Counter()
    call_params = {}
    forced_update = False

    def forced_update_func(a, b):
        call_counter[1] += 1
        call_params[call_counter[1] - 1] = (a, b)

        return forced_update

    @cache.memoize(5, forced_update=forced_update_func)
    def memoized_func(a, b):
        return a + b + random.randrange(0, 100000)

    # Save the value for later inspection
    result = memoized_func(5, 2)
    # forced_update_func should have been called twice; once by memoize itself, once by
    # _memoize_version…
    assert call_counter[1] == 2
    # …with the values we called the function with
    assert call_params[0] == (5, 2)
    assert call_params[1] == (5, 2)
    time.sleep(1)

    # Calling the function again should return the cached value
    assert memoized_func(5, 2) == result
    # forced_update_func should have been called two more times…
    assert call_counter[1] == 4
    # …with the values we called the function with
    assert call_params[2] == (5, 2)
    assert call_params[3] == (5, 2)

    # Tell forced_update_func to return True next time
    forced_update = True
    # Save the new result…
    new_result = memoized_func(5, 2)
    # …which, due to the random number in the function, should be different from the old one
    assert new_result != result
    # forced_update_func should have been called two more times again…
    assert call_counter[1] == 6
    # …with the values we called the function with
    assert call_params[4] == (5, 2)
    assert call_params[5] == (5, 2)

    # Now stop forced updating again
    forced_update = False
    time.sleep(1)
    # The function should return the same value as it did last time
    assert memoized_func(5, 2) == new_result
    # forced_update_func should have been called two more times again…
    assert call_counter[1] == 8
    # …with the values we called the function with
    assert call_params[6] == (5, 2)
    assert call_params[7] == (5, 2)


def test_memoize_multiple_arg_kwarg_calls(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b, c=[1, 1], d=[1, 1]):
        return sum(a) + sum(b) + sum(c) + sum(d) + random.randrange(0, 100000)  # noqa

    result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])

    assert big_foo([5, 3, 2], [1], d=[3, 3], c=[3, 3]) == result_a
    assert big_foo(b=[1], a=[5, 3, 2], c=[3, 3], d=[3, 3]) == result_a
    assert big_foo([5, 3, 2], [1], [3, 3], [3, 3]) == result_a


def test_memoize_multiple_arg_kwarg_delete(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b, c=[1, 1], d=[1, 1]):
        return sum(a) + sum(b) + sum(c) + sum(d) + random.randrange(0, 100000)  # noqa

    result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
    cache.delete_memoized(big_foo, [5, 3, 2], [1], [3, 3], [3, 3])
    result_b = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
    assert result_a != result_b

    cache.delete_memoized(big_foo, [5, 3, 2], b=[1], c=[3, 3], d=[3, 3])
    result_b = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
    assert result_a != result_b

    cache.delete_memoized(big_foo, [5, 3, 2], [1], c=[3, 3], d=[3, 3])
    result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
    assert result_a != result_b

    cache.delete_memoized(big_foo, [5, 3, 2], b=[1], c=[3, 3], d=[3, 3])
    result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
    assert result_a != result_b

    cache.delete_memoized(big_foo, [5, 3, 2], [1], c=[3, 3], d=[3, 3])
    result_b = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
    assert result_a != result_b

    cache.delete_memoized(big_foo, [5, 3, 2], [1], [3, 3], [3, 3])
    result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
    assert result_a != result_b


def test_memoize_kwargs_to_args(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    def big_foo(a, b, c=None, d=None):
        return sum(a) + sum(b) + random.randrange(0, 100000)

    expected = (1, 2, 'foo', 'bar')

    args, kwargs = cache._memoize_kwargs_to_args(big_foo, 1, 2, 'foo', 'bar')
    assert (args == expected)
    args, kwargs = cache._memoize_kwargs_to_args(big_foo, 2, 'foo', 'bar', a=1)
    assert (args == expected)
    args, kwargs = cache._memoize_kwargs_to_args(big_foo, a=1, b=2, c='foo', d='bar')
    assert (args == expected)
    args, kwargs = cache._memoize_kwargs_to_args(big_foo, d='bar', b=2, a=1, c='foo')
    assert (args == expected)
    args, kwargs = cache._memoize_kwargs_to_args(big_foo, 1, 2, d='bar', c='foo')
    assert (args == expected)


def test_memoize_when_using_args_unpacking(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(*args):
        return sum(args) + random.randrange(0, 100000)

    result_a = big_foo(1, 2)
    result_b = big_foo(1, 3)

    assert big_foo(1, 2) == result_a
    assert big_foo(1, 3) == result_b
    assert big_foo(1, 2) != result_b
    assert big_foo(1, 3) != result_a

    cache.delete_memoized(big_foo)

    assert big_foo(1, 2) != result_a
    assert big_foo(1, 3) != result_b


def test_memoize_when_using_variable_mix_args_unpacking(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    @cache.memoize()
    def big_foo(a, b, *args, **kwargs):
        return sum([a, b]) + sum(args) + sum(kwargs.values()) + random.randrange(0, 100000)

    result_a = big_foo(1, 2, 3, 4, x=2, y=5)
    result_b = big_foo(4, 7, 7, 2, x=1, y=4)

    assert big_foo(1, 2, 3, 4, x=2, y=5) == result_a
    assert big_foo(4, 7, 7, 2, x=1, y=4) == result_b
    assert big_foo(1, 2, 3, 4, x=2, y=5) != result_b
    assert big_foo(4, 7, 7, 2, x=1, y=4) != result_a

    cache.delete_memoized(big_foo)

    assert big_foo(1, 2, 3, 4, x=2, y=5) != result_a
    assert big_foo(4, 7, 7, 2, x=1, y=4) != result_b


def test_memoize_none(app, caches):
    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return
    if cache.config['CACHE_TYPE'] in ['redissentinel', 'redis']:
        return

    from collections import Counter

    call_counter = Counter()

    @cache.memoize(cache_none=True)
    def memoize_none(param):
        call_counter[param] += 1

        return None

    memoize_none(1)

    # The memoized function should have been called
    assert call_counter[1] == 1

    # Next time we call the function, the value should be coming from the cache…
    assert memoize_none(1) is None

    # …thus, the call counter should remain 1
    assert call_counter[1] == 1

    cache.clear()

    memoize_none(1)
    assert call_counter[1] == 2


def test_memoize_never_accept_none(app, caches):
    """Asserting that when cache_none is False, we always
       assume a None value returned from .get() means the key is not found
    """
    from collections import Counter

    # it is sufficient to test it with one type of cache
    cache = caches['time-based']

    # skip the test for memcached
    if cache.config['CACHE_TYPE'] in ['memcached', 'gaememcached', 'saslmemcached', 'spreadsaslmemcached']:
        return

    call_counter = Counter()

    @cache.memoize()
    def memoize_none(param):
        call_counter[param] += 1

        return None

    memoize_none(1)

    # The memoized function should have been called
    assert call_counter[1] == 1

    # Next time we call the function, the value should be coming from the cache…
    # But the value is None and so we treat it as uncached.
    assert memoize_none(1) is None

    # …thus, the call counter should increment to 2
    assert call_counter[1] == 2

    cache.clear()

    memoize_none(1)
    assert call_counter[1] == 3
