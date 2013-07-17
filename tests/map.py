#!/usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import unittest
import lsst.utils.tests as utilsTests

import os
from lsst.obs.test import TestMapper

# map_raw(self, dataId)
# query_raw(self, key, format, dataId)
# std_raw(self, item)
# keys(self)
# 
# __init__(self)
# getDatasetTypes(self)
# map(self, datasetType, dataId)
# queryMetadata(self, datasetType, key, format, dataId)
# canStandardize(self, datasetType)
# standardize(self, datasetType, item, dataId)
# validate(self, dataId)

class TestMapperTestCase(unittest.TestCase):
    """A test case for the test mapper."""

    def setUp(self):
        self.input = os.path.join(os.environ['OBS_TEST_DIR'],
                "tests", "data", "input")
        self.calib = os.path.join(os.environ['OBS_TEST_DIR'],
                "tests", "data", "calib")
        self.output = os.path.join(os.environ['OBS_TEST_DIR'],
                "tests", "data", "output")
        self.mapper = TestMapper(root=self.input,
                calibRoot=self.calib,
                outputRoot=self.output)

    def tearDown(self):
        del self.mapper


    def testMapRaw(self):
        dataId = dict(visit=85470982,
                raft="0,3", sensor="0,1", channel="0,0", snap=1)
        loc = self.mapper.map_raw(dataId)
        self.assertEqual(loc.getPythonType(), None)
        self.assertEqual(loc.getCppType(), "ImageU")
        self.assertEqual(loc.getStorageName(), "PickleStorage")
        self.assertEqual(loc.getLocations(), [os.path.join(self.input,
            "raw-v85470982-E001-r0,3-s0,1-c0,0.pickle")])
        for k, v in dataId.iteritems():
            self.assertEqual(loc.getAdditionalData().get(k), v)

    def testQueryRawData(self):
        tuples = self.mapper.query_raw("raft", ["visit", "raft"], dict())
        self.assertEqual(tuples, set([
            (85470982, "0,1"), (85470982, "0,2"), (85470982, "0,3"),
            ]))

        tuples = self.mapper.query_raw("channel",
                ["raft", "sensor", "channel"],
                dict(visit=85470982, raft="0,1"))
        self.assertEqual(tuples, set([
            ("0,1", "0,1", "0,0"),
            ("0,1", "0,1", "0,1"),
            ("0,1", "0,1", "1,0"),
            ("0,1", "0,1", "1,1"),
            ("0,1", "1,0", "0,0"),
            ("0,1", "1,0", "0,1"),
            ("0,1", "1,0", "1,0"),
            ("0,1", "1,0", "1,1"),
            ("0,1", "1,1", "0,0"),
            ("0,1", "1,1", "0,1"),
            ("0,1", "1,1", "1,0"),
            ("0,1", "1,1", "1,1"),
            ]))

    def testStdRawData(self):
        dataId = dict(visit=85470982,
                snap=1, raft="0,2", sensor="1,0", channel="0,1")
        self.assertEqual(self.mapper.std_raw(210011, dataId),
                '210011/85470982')

    def testMapConfigData(self):
        dataId = dict(visit=85470982, raft="0,2", sensor="1,1")
        loc = self.mapper.map_processCcd_config(dataId)
        self.assertEqual(loc.getPythonType(), "lsst.obs.test.TestConfig")
        self.assertEqual(loc.getCppType(), "Config")
        self.assertEqual(loc.getStorageName(), "ConfigStorage")
        self.assertEqual(loc.getLocations(), [os.path.join(self.output,
            "config", "processCcd.py")])
        for k, v in dataId.iteritems():
            self.assertEqual(loc.getAdditionalData().get(k), v)

    def testMapMetadataData(self):
        dataId = dict(visit=85470982, raft="0,1", sensor="1,0")
        loc = self.mapper.map_processCcd_metadata(dataId)
        self.assertEqual(loc.getPythonType(), "lsst.daf.base.PropertySet")
        self.assertEqual(loc.getCppType(), "PropertySet")
        self.assertEqual(loc.getStorageName(), "BoostStorage")
        self.assertEqual(loc.getLocations(), [os.path.join(self.output,
            "md-v85470982-r0,1-s1,0.boost")])
        for k, v in dataId.iteritems():
            self.assertEqual(loc.getAdditionalData().get(k), v)

    def testKeys(self):
        self.assertEqual(set(self.mapper.keys()),
                set(['skyTile', 'visit', 'raft', 'sensor', 'snap', 'channel']))

    def testGetDatasetTypes(self):
        self.assertEqual(set(self.mapper.getDatasetTypes()),
                set(['raw', 'processCcd_config', 'processCcd_metadata']))

    def testGetKeys(self):
        self.assertEqual(set(self.mapper.getKeys("raw", "skyTile")),
                set(["skyTile"]))
        self.assertEqual(set(self.mapper.getKeys("raw", "visit")),
                set(["skyTile", "visit"]))
        self.assertEqual(set(self.mapper.getKeys("raw", "raft")),
                set(["skyTile", "visit", "raft"]))
        self.assertEqual(set(self.mapper.getKeys("raw", "sensor")),
                set(["skyTile", "visit", "raft", "sensor"]))
        self.assertEqual(set(self.mapper.getKeys("raw", "snap")),
                set(["skyTile", "visit", "raft", "sensor", "snap"]))
        self.assertEqual(set(self.mapper.getKeys("raw", "channel")),
                set(["skyTile", "visit", "raft", "sensor", "snap", "channel"]))

    def testGetDefaultLevel(self):
        self.assertEqual(self.mapper.getDefaultLevel(), "sensor")

    def testGetDefaultSubLevel(self):
        self.assertEqual(self.mapper.getDefaultSubLevel("skyTile"), "sensor")
        self.assertEqual(self.mapper.getDefaultSubLevel("visit"), "sensor")
        self.assertEqual(self.mapper.getDefaultSubLevel("raft"), "sensor")
        self.assertEqual(self.mapper.getDefaultSubLevel("snap"), None)
        self.assertEqual(self.mapper.getDefaultSubLevel("sensor"), "channel")
        self.assertEqual(self.mapper.getDefaultSubLevel("channel"), None)

    def testMap(self):
        dataId = dict(visit=85470982,
                raft="0,2", sensor="0,1", channel="1,1", snap=0)
        loc = self.mapper.map("raw", dataId)
        self.assertEqual(loc.getPythonType(), None)
        self.assertEqual(loc.getCppType(), "ImageU")
        self.assertEqual(loc.getStorageName(), "PickleStorage")
        self.assertEqual(loc.getLocations(), [os.path.join(self.input,
            "raw-v85470982-E000-r0,2-s0,1-c1,1.pickle")])
        for k, v in dataId.iteritems():
            self.assertEqual(loc.getAdditionalData().get(k), v)

        dataId = dict(visit=85470982, raft="0,3", sensor="1,1")
        loc = self.mapper.map("processCcd_config", dataId)
        self.assertEqual(loc.getPythonType(), "lsst.obs.test.TestConfig")
        self.assertEqual(loc.getCppType(), "Config")
        self.assertEqual(loc.getStorageName(), "ConfigStorage")
        self.assertEqual(loc.getLocations(), [os.path.join(self.output,
            "config", "processCcd.py")])
        for k, v in dataId.iteritems():
            self.assertEqual(loc.getAdditionalData().get(k), v)

    def testQueryMetadata(self):
        tuples = self.mapper.queryMetadata("raw", "sensor",
                ["skyTile", "visit", "raft", "sensor"],
                dict(raft="0,3", sensor="0,1", visit=85470982))
        self.assertEqual(tuples, set([(1, 85470982, "0,3", "0,1")]))

        tuples = self.mapper.queryMetadata("raw", "sensor",
                ["skyTile", "visit", "raft", "sensor"], dict(visit=85470982))
        self.assertEqual(tuples, set([
            (1, 85470982, "0,1", "0,1"),
            (1, 85470982, "0,1", "1,0"),
            (1, 85470982, "0,1", "1,1"),
            (1, 85470982, "0,2", "0,1"),
            (1, 85470982, "0,2", "1,0"),
            (1, 85470982, "0,2", "1,1"),
            (1, 85470982, "0,3", "0,1"),
            (1, 85470982, "0,3", "1,0"),
            (1, 85470982, "0,3", "1,1")]))

    def testCanStandardize(self):
        self.assertEqual(self.mapper.canStandardize("raw"), True)
        self.assertEqual(self.mapper.canStandardize("processCcd_config"),
                False)
        self.assertEqual(self.mapper.canStandardize("processCcd_metadata"),
                False)

    def testStandardize(self):
        dataId = dict(visit=12345)
        self.assertEqual(self.mapper.standardize("raw", 9876, dataId),
                '9876/12345')

    def testValidate(self):
        for dataId in [
                dict(visit=85470982,
                    raft="0,3", sensor="0,1", channel="0,0", snap=1),
                dict(visit=85470982, raft="0,2", sensor="1,1"),
                dict(visit=85470982, raft="0,1", sensor="1,0"),
                dict(visit=85470982,
                    raft="0,2", sensor="0,1", channel="1,1", snap=0),
                dict(visit=85470982, raft="0,3", sensor="1,1"),]:
            self.assertEqual(self.mapper.validate(dataId), dataId)
        for dataId in [
                dict(visit=85470982,
                    raft="0.3", sensor="0,1", channel="0,0", snap=1),
                dict(visit=85470982, raft="0,2", sensor="11"),
                dict(visit=85470982, raft="x,1", sensor="1,0"),
                dict(visit=85470982,
                    raft="0,2", sensor="0,1", channel="1,1", snap="0"),
                dict(visit="85470982", raft="0,3", sensor="1,1"),
                dict(visit=85470982,
                    raft=03, sensor="0,1", channel="0,0", snap=1),
                ]:
            try:
                self.mapper.validate(dataId)
                self.assert_(False,
                        msg="%s failed to raise exception" % str(dataId))
            except AssertionError:
                raise
            except Exception, e:
                self.assertIsInstance(e, RuntimeError)


def suite():
    utilsTests.init()

    suites = []
    suites += unittest.makeSuite(TestMapperTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(shouldExit=False):
    utilsTests.run(suite(), shouldExit)

if __name__ == '__main__':
    run(True)
