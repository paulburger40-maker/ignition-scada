"""Real electrical history arithmetic; fixed South Africa civil-day boundaries."""
import calendar,datetime,math
DAY=86400000
MINUTE=60000
OFFSET=7200000
MAX_GAP=20000

def finite(value):
    if isinstance(value,bool): raise ValueError('Boolean measurement')
    number=float(value)
    if math.isnan(number) or math.isinf(number) or number<0: raise ValueError('Invalid measurement')
    return number

def day_start(timestamp):
    return ((int(timestamp)+OFFSET)//DAY)*DAY-OFFSET

def month_start(year,month):
    return int(calendar.timegm((year,month,1,0,0,0))*1000)-OFFSET

def months(now,count=12):
    local=datetime.datetime.utcfromtimestamp((now+OFFSET)/1000.0)
    index=local.year*12+local.month-1
    result=[]
    for i in range(index-count+1,index+1):
        year,month=divmod(i,12);month+=1
        ny,nm=divmod(i+1,12)
        result.append(dict(key='%04d-%02d'%(year,month),label=datetime.date(year,month,1).strftime('%b %y'),
            start=month_start(year,month),end=month_start(ny,nm+1)))
    return result

def utc_iso(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp/1000.0).strftime('%Y-%m-%dT%H:%M:%SZ')

def parse_utc(value):
    if not isinstance(value,str): value=str(value)
    # Accept the documented UTC format and optional fractional seconds only.
    if not value.endswith('Z'): raise ValueError('UTC interval required')
    body=value[:-1].split('.')[0]
    dt=datetime.datetime.strptime(body,'%Y-%m-%dT%H:%M:%S')
    return int(calendar.timegm(dt.timetuple())*1000)

def integrate(previous,current):
    """Trapezoids between adjacent real samples; never bridge an outage."""
    a,b=int(previous['ts_ms']),int(current['ts_ms'])
    if b<=a or b-a>MAX_GAP: return []
    p0,p1=finite(previous['power_w']),finite(current['power_w'])
    segments=[];start=a
    while start<b:
        minute=(start//MINUTE)*MINUTE
        end=min(b,minute+MINUTE)
        left=p0+(p1-p0)*(start-a)/float(b-a)
        right=p0+(p1-p0)*(end-a)/float(b-a)
        segments.append((minute,(left+right)*0.5*(end-start)/3600000000.0,end-start))
        start=end
    return segments

def intervals(payload,start,end,resolution=3600):
    """Validate meter kWh records without inventing allocations across civil days."""
    result=[]
    for row in payload:
        a,b=parse_utc(row['start']),parse_utc(row['end'])
        usage=finite(row['usage'])/100.0
        if a<start or b>end or b<=a or b-a<resolution*1000: continue
        if a%MINUTE or b%MINUTE or b>day_start(a)+DAY: continue
        result.append((a,b,usage))
    result.sort()
    if any(result[i][0]<result[i-1][1] for i in range(1,len(result))):
        raise ValueError('Overlapping meter energy intervals')
    return result

def bars(aggregates,now,monthly=False):
    lookup={str(r['period']):r for r in aggregates}
    if monthly: periods=months(now)
    else:
        first=day_start(now)-6*DAY;periods=[]
        for i in range(7):
            start=first+i*DAY;dt=datetime.datetime.utcfromtimestamp((start+OFFSET)/1000.0)
            periods.append(dict(key=dt.strftime('%Y-%m-%d'),label=dt.strftime('%d %b'),start=start,end=start+DAY))
    result=[]
    for period in periods:
        row=lookup.get(period['key']);covered=int(row['covered_ms']) if row else 0
        estimated=int(row['estimated_ms']) if row else 0
        elapsed=max(1,min(now,period['end'])-period['start'])
        coverage=min(100.0,100.0*covered/elapsed)
        complete=period['end']<=now and covered>=period['end']-period['start']-1000
        result.append(dict(period=period['label'],energy_kwh=round(float(row['kwh']),3) if row and covered else None,
            coverage=('%0.1f%% recorded'%coverage) if covered else 'No data',
            completeness='Complete' if complete else ('In progress / partial' if covered else 'No data'),
            basis='Includes power-based estimate' if estimated else ('Meter energy' if covered else 'No data'),
            bar_color='#168a91' if complete else '#8dbec2'))
    return result
