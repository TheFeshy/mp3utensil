# pylint: disable=trailing-whitespace, import-error

"""This file aggregates and runs all the test cases found in the test
   directory.  It is used for unittest validation."""

import unittest
 
from test_mp3header import Test_MP3Header  # @UnresolvedImport
from test_mp3framelist import Test_MP3FrameList  # @UnresolvedImport
from test_mp3file import Test_MP3File  # @UnresolvedImport

def build_test_suites():
    """Builds three suites of tests, one for all the short tests, medium 
       tests, and long tests."""
    my_test_suites = {}
    test_cases = [Test_MP3File] #header, framelist
    test_types = ['short', 'medium', 'long']
    for t_type in test_types:
        suite = unittest.TestSuite()
        for case in test_cases:
            suite.addTest(unittest.makeSuite(case, 'test_{0}'.format(t_type)))
        my_test_suites[t_type] = suite
    return my_test_suites

def run_testcase(case):
    """Runs a single test"""
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(case, 'test'))
    runner.run(suite)

def run_suite(suite, name = '', skipif=False):
    """runs a suit of tests, or optionally skips all the tests"""
    if skipif:
        print("Failed previous tests, skipping {0}".format(name))
    else:
        runner = unittest.TextTestRunner()
        #print("Running suite {0}".format(name))
        testresults = runner.run(suite)
        if testresults.failures or testresults.errors:
            return False
        else:
            return True 
        
def run_all(): 
    """Runs all suites of tests built by build_test_suites"""      
    skipif = False
    suites = build_test_suites()
    print("Running all available tests")
    for name, suite in suites.items():
        skipif = not run_suite(suite, name, skipif)
if __name__ == '__main__':
    
    run_all()
