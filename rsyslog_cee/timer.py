import json
import time
from typing import Optional
from json import JSONEncoder

class TimeKept():
  start: float
  stop:  float
  range: float

  def __init__(self,start: float,stop: float,range: float):
    self.start = start
    self.stop  = stop
    self.range = range

  def asdict(self):
        return {'start': self.start, 'stop': self.stop, 'range': self.range }    

  def toJson(self):
    return json.dumps(dict(self))

class TimeKeeper():
  _label: str
  _start: float

  _stop:  float
  _range: Optional[float]

  def __init__(self,sLabel: str):
    self._label = sLabel
    self._start = TimeKeeper.getTime()
    self._stop  = 0
    self._range = None
  
  @staticmethod
  def getTime() -> float:
    return time.time() * 1000 # ms
  

  def range(self) -> float:
    if self._range is None:
      if self._stop > 0:
        self._range = self._stop - self._start
      else:
        self._range = TimeKeeper.getTime() - self._start
    return self._range

  def stop(self) -> float:
    self._stop = TimeKeeper.getTime()
    return self.range()

  def label(self) -> str:
    return self._label

  def getStart(self) -> float:
    return self._start

  def started(self) -> bool:
    return self._start > 0

  def toJson(self):
    return TimeKept(self._start,self._stop,self.range()).toJson()

class TimerInfo:
  range:   float = 0
  count:   float = 0
  average: float = 0
  timers:  [Optional[TimeKept]] = []

  def __init__(self,range=0,count=0,average=0,timers=[]):
    self.range = range
    self.count = count
    self.average = average
    self.timers = timers

  def toJson(self):
    hout = {}
    hout['range'] = self.range
    hout['count'] = self.count
    hout['average'] = self.average
    otimers = []
    for oTimer in self.timers:
      otimers = oTimer.toJson() 
    hout['timers'] = otimers
    return json.dumps(hout)


class Timer:
  bReturnTimers:  bool

  oTimers: {}   # { str => TimeKeeper}
  oIndices: {}  # { str => int}

  def __init__(self,bReturnTimers: bool = False):
    self.oTimers        = {}
    self.oIndices       = {}
    self.bReturnTimers  = bReturnTimers
  

  def shouldReturnTimers(self,bReturnTimers: bool):
    self.bReturnTimers = bReturnTimers;

  def get(self,sLabel: str) -> Optional[TimerInfo]:
    if sLabel in self.oTimers and len(self.oTimers[sLabel]) > 0:
      aTimers = self.oTimers[sLabel]
      oReturn = TimerInfo(range=0,count=0,average=0)
      for oTime in aTimers:
        if oTime.started():
          oReturn.range += oTime.range()
          oReturn.count += 1
          if self.bReturnTimers:
            if not oReturn.timers:
              oReturn.timers = []
            oReturn.timers.append(oTime)

      oReturn.average = oReturn.range / oReturn.count
      return oReturn

  def getAll(self):
    oReturn = {}
    for sLabel in self.oTimers.keys():
      oTimer = self.get(sLabel)
      if oTimer:
        oReturn[sLabel] = oTimer.toJson()
    return oReturn

  def find(self,sLabel: str):
      return self.oTimers[sLabel][self.oIndices[sLabel]]

  def start(self,sLabel: str):
    oTime = TimeKeeper(sLabel)
    if sLabel not in self.oTimers:
      self.oTimers[sLabel] = [oTime]
    else:
      self.oTimers[sLabel].append(oTime)
    self.oIndices[sLabel] = len(self.oTimers[sLabel]) - 1
    return oTime

  def stop(self,sLabel: str):
    oTime = self.find(sLabel)
    oTime.stop()
    return oTime.range()
