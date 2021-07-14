#!/data/leuven/320/vsc32093/miniconda3/envs/science/bin/python

from datetime import datetime, tzinfo, timedelta


class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)
    def dst(self, dt):
        return timedelta(0)

class CEST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)
    def dst(self, dt):
        dston = datetime(year=dt.year, month=3, day=20)
        dstoff = datetime(year=dt.year, month=10, day=20)
        if dston <= dt.replace(tzinfo=None) < dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)

class CET(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1)
    def dst(self, dt):
        return timedelta(hours=1)

class EAT(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=3)
    def dst(self, dt):
        return timedelta(hours=3)


def from_cest_to_utc(year, month, day, hour, minute):
    cest = datetime(year, month, day, hour, minute, tzinfo=CEST())
    utc = cest.astimezone(tz=UTC())
    return '{:%Y-%m-%d:T%H:%MZ}'.format(utc)

def from_cet_to_eat(year, month, day, hour, minute):
    cet = datetime(year, month, day, hour, minute, tzinfo=CET())
    eat = cet.astimezone(tz=EAT())
    return '{:%Y-%m-%d:T%H:%MZ}'.format(eat)

def from_cest_to_eat(year, month, day, hour, minute):
    cest = datetime(year, month, day, hour, minute, tzinfo=CEST())
    eat = cest.astimezone(tz=EAT())
    return '{:%Y-%m-%d:T%H:%MZ}'.format(eat)

def CEST2EAT(d):
    eatstr=from_cest_to_eat(year=d.year, month=d.month, day=d.day, hour=d.hour, minute=d.minute)
    d_eat=datetime.strptime(eatstr,'%Y-%m-%d:T%H:%MZ')
    return d_eat

def CET2EAT(d):
    eatstr=from_cet_to_eat(year=d.year, month=d.month, day=d.day, hour=d.hour, minute=d.minute)
    d_eat=datetime.strptime(eatstr,'%Y-%m-%d:T%H:%MZ')
    return d_eat
