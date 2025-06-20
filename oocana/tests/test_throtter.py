import unittest
from ..oocana.throttler import throttle
import time
class TestThrottle(unittest.TestCase):
    
    def test_throttle(self):
        
        a = 0

        @throttle(1)
        def test_fn(i):
            nonlocal a
            a = i

        self.assertEqual(a, 0)
        test_fn(1)
        self.assertEqual(a, 1)

        test_fn(2)
        self.assertEqual(a, 1)
        test_fn(3)
        self.assertEqual(a, 1)
        
        time.sleep(1.1)
        self.assertEqual(a, 3)

        test_fn(4)
        test_fn(5)
        test_fn(6)

        time.sleep(1.1)
        self.assertEqual(a, 6)

        test_fn(7)
        time.sleep(1.1)
        self.assertEqual(a, 7)