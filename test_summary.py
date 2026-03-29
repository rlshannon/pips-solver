#!/usr/bin/env python
"""Quick summary of Phase 3 tests."""

import unittest
import sys

loader = unittest.TestLoader()
suite = loader.loadTestsFromName('test_generator')
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)

print(f"\n{'='*60}")
print(f"PHASE 3 TEST SUMMARY")
print(f"{'='*60}")
print(f"Tests Run: {result.testsRun}")
print(f"Failures: {len(result.failures)}")
print(f"Errors: {len(result.errors)}")
print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

if result.failures:
    print(f"\nFailed tests:")
    for test, _ in result.failures:
        print(f"  - {test}")

if result.errors:
    print(f"\nError tests:")
    for test, _ in result.errors:
        print(f"  - {test}")
