import time
from typing import Optional

class TimeKept:
  start: float
  stop:  float
  range: float

  def __init__(self,start: float,stop: float,range:  float):
    self.start = start
    self.stop  = stop
    self.range = range

class TimeKeeper:
  _label: str
  _start: float

  _stop:  float
  _range: float

  def __init__(self,sLabel: str):
    self._label = sLabel
    self._start = TimeKeeper.getTime()
    self._stop  = 0
    self._range = 0
  
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

  def toObject() -> TimeKept:
    return TimeKept(self._start,self._stop,self.range())

class TimerInfo:
  range:   float
  count:   float
  average: float
  timers:  [Optional[TimeKept]]

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
      oReturn: TimerInfo(range=0,count=0,average=0)
      for oTime in aTimers:
        if oTime.started():
          oReturn.range += oTime.range()
          oReturn.count += 1
          if self.bReturnTimers:
            if not oReturn.timers:
              oReturn.timers = []
            oReturn.timers.append(oTime.toObject())

      oReturn.average = oReturn.range / oReturn.count
      return oReturn

  def getAll(self):
    oReturn = {}
    for sLabel in self.oTimers.keys():
      oTimer = self.get(sLabel)
      if oTimer:
        oReturn[sLabel] = oTimer
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
