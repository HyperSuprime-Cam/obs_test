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

import os
import re

import lsst.daf.base as dafBase
import lsst.daf.persistence as dafPersist

__all__ = ["TestMapper"]

class TestMapper(dafPersist.Mapper):
    def __init__(self, root=None, calibRoot=None, outputRoot=None, **kwargs):
        super(TestMapper, self).__init__()
        self.root = root
        self.calibRoot = calibRoot
        if outputRoot is None:
            outputRoot = root
        self.outputRoot = outputRoot
        self.keyDict = dict(
                skyTile=int,
                visit=int,
                raft=str,
                sensor=str,
                snap=int,
                channel=str
                )
        self.levels = dict(
                skyTile=['visit', 'raft', 'sensor', 'snap', 'channel'],
                visit=['snap', 'raft', 'sensor', 'channel'],
                raft=['snap', 'sensor', 'channel'],
                sensor=['snap', 'channel'],
                snap=['channel']
                )
        self.defaultLevel = 'sensor'
        self.defaultSubLevels = dict(
                skyTile='sensor',
                visit='sensor',
                raft='sensor',
                sensor='channel'
                )
        self.dictList = []
        for raft in ["0,1", "0,2", "0,3"]:
            for sensor in ["0,1", "1,0", "1,1"]:
                for snap in [0, 1]:
                    for channel in ["0,0", "0,1", "1,0", "1,1"]:
                        self.dictList.append(dict(
                            skyTile=1,
                            visit=85470982,
                            raft=raft,
                            sensor=sensor,
                            snap=snap,
                            channel=channel
                            ))


    def keys(self):
        return self.keyDict.iterkeys()

    def getKeys(self, datasetType, level):
        keyDict = self.keyDict
        if level is not None and level in self.levels:
            keyDict = dict(keyDict)
            for l in self.levels[level]:
                if l in keyDict:
                    del keyDict[l]
        return keyDict

    @classmethod
    def getCameraName(cls):
        return "test"
    
    @classmethod
    def getEupsProductName(cls):
        return "obs_test"

    def getDefaultLevel(self):
        return self.defaultLevel

    def getDefaultSubLevel(self, level):
        if level in self.defaultSubLevels:
            return self.defaultSubLevels[level]
        return None

    def validate(self, dataId):
        for component in ("raft", "sensor", "channel"):
            if component not in dataId:
                continue
            id = dataId[component]
            if not isinstance(id, str):
                raise RuntimeError, \
                        "%s identifier should be type str, not %s: %s" % \
                        (component.title(), type(id), repr(id))
            if not re.search(r'^(\d),(\d)$', id):
                raise RuntimeError, \
                        "Invalid %s identifier: %s" % (component, repr(id))
        for component in ("visit", "snap"):
            if component not in dataId:
                continue
            id = dataId[component]
            if not isinstance(id, int) and not isinstance(id, long):
                raise RuntimeError, \
                        "%s identifier should be int or long, not %s: %s" % \
                        (component.title(), type(id), repr(id))
            if component == "snap":
                if id < 0 or id > 1:
                    raise RuntimeError, \
                            "Invalid snap identifier: %d" % (id,)

        return dataId

    def map_raw(self, dataId, write=False):
        loc = "raw-v%(visit)d-E%(snap)03d-r%(raft)s-s%(sensor)s-c%(channel)s.pickle" % dataId
        loc = os.path.join(self.root, loc)
        return dafPersist.ButlerLocation(None, "ImageU", "PickleStorage",
                [loc], dataId)

    def std_raw(self, object, dataId):
        return str(object) + "/" + str(dataId['visit'])

    def map_processCcd_config(self, dataId, write=False):
        loc = "config/processCcd.py"
        loc = os.path.join(self.outputRoot, loc)
        return dafPersist.ButlerLocation("lsst.obs.test.TestConfig", "Config", "ConfigStorage",
                [loc], dataId)

    def map_processCcd_metadata(self, dataId, write=False):
        loc = "md-v%(visit)d-r%(raft)s-s%(sensor)s.boost" % dataId
        loc = os.path.join(self.outputRoot, loc)
        return dafPersist.ButlerLocation(
                "lsst.daf.base.PropertySet", "PropertySet", "BoostStorage",
                [loc], dataId)

    def query_raw(self, level, format, dataId):
        result = set()
        for d in self.dictList:
            where = True
            for k in dataId.iterkeys():
                if k not in d:
                    raise RuntimeError("%s not in %s" % (k, repr(d)))
                if d[k] != dataId[k]:
                    where = False
                    break
            if where:
                values = []
                for k in format:
                    values.append(d[k])
                result.add(tuple(values))
        return result
