from pprint import pprint
from skyfield.api import Topos, load, load_file, N, W, wgs84
from skyfield import almanac
from datetime import timedelta, datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from pytz import timezone
import datetime as dt
import statistics

# Global objects
ts = load.timescale()
# planets = load('de440.bsp')
# eph = load_file('/var/data/de421.bsp')
eph = load_file('/var/data/de440.bsp')
# eph = load_file('/var/data/de440.bsp')
earth = eph['earth']
sun = eph['sun']
eastern = timezone('US/Eastern')

def find_harvest_moon(startyear=2021, years=100):
    '''
    find days between closest full Moon and the September equinox
    '''
    t0 = ts.utc(startyear-int(years/2), 1, 1)
    t1 = ts.utc(startyear+int(years/2), 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(eph))

    deltas=[]
    deltas={}
    for yi, ti in zip(y, t): #iterate over seasons
        if yi != 2:
            continue
        lunation = ts.utc(ti.utc_datetime().year, ti.utc_datetime().month,
                          range(ti.utc_datetime().day-15, ti.utc_datetime().day+15))
        tm, ym = almanac.find_discrete(lunation[0], lunation[-1], almanac.moon_phases(eph))
        for tmi, ymi in zip(tm,ym): #iterate over phases
            if ymi != 2:  # not full
                continue
            delta=abs(tmi-ti)
            deltas[ti.utc_iso(' ')]=delta
    for date, delta in dict(sorted(deltas.items(), key=lambda item: item[1])).items():
        print(f" {date} {delta:12.4f}")


def find_full_moons(year=2021):
    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    results = []
    for ti, yi in zip(t,y):
        if yi != 2:
            continue
        results.append(ti.utc_datetime())
        # results.append(ti)
    return results

def moonrise():
    '''
    calculates how much later throughout the year that the Moon rises around a full moon
    '''
    fms=find_full_moons()
    # Use a breakpoint in the code line below to debug your script.
    # for fm in find_full_moons():
    # 35.7796° N, 78.6382° W
    for fm in fms:
        print('-'*20)
        print(f'full moon: {fm.astimezone(eastern).strftime("%c")}')
        t0 = ts.utc(fm.year, fm.month, fm.day-2)  #3 days before and after day of full moon
        t1 = ts.utc(fm.year, fm.month, fm.day+4)
        observer = wgs84.latlon(+35.78, -78.64)

        fmoon = almanac.risings_and_settings(eph, eph['Moon'], observer)
        tmoon, ymoon = almanac.find_discrete(t0, t1, fmoon)

        fsun = almanac.risings_and_settings(eph, eph['Sun'], observer)
        tsun, ysun = almanac.find_discrete(t0, t1, fsun)
        prev = 0
        deltas=[]
        for i in range(len(tmoon)):
            if ymoon[i] == 1: #moonrise
                hour = int(tmoon[i].astimezone(eastern).strftime("%-H"))
                minute = int(tmoon[i].astimezone(eastern).strftime("%-M"))
                ttt = hour + (minute / 60.0)
                if prev != 0:
                    delta = ttt - prev
                    deltas.append(delta*60)
                else:
                    delta=0
                prev = ttt
                print(f'moonrise: {tmoon[i].astimezone(eastern).strftime("%c")}  sunset {tsun[i].astimezone(eastern).strftime("%c")} {delta*60:12.2f}')
        print(f"mean minutes later {statistics.mean(deltas):12.2f}")

if __name__ == '__main__':
    print ('Moonrise daily delta')
    moonrise()

    print ('Sept full Moon to equinox delta')
    find_harvest_moon()
