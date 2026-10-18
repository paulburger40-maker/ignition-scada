"""Dedicated Ignition SQLite connection; real samples and verified meter intervals."""
import datetime,threading,time,sys
DB='Home_Energy_SQLite'
_lock=threading.RLock()
_ready=False
_cache={}
_owner=object()
KEY='cottage_history_worker_v1'

def ensure():
    global _ready
    with _lock:
        if _ready:return
        for sql in [
            'CREATE TABLE IF NOT EXISTS power_samples(ts_ms INTEGER PRIMARY KEY,power_w REAL NOT NULL,voltage_v REAL,current_a REAL)',
            'CREATE TABLE IF NOT EXISTS minute_energy(minute_ms INTEGER PRIMARY KEY,kwh REAL NOT NULL,covered_ms INTEGER NOT NULL)',
            'CREATE TABLE IF NOT EXISTS meter_energy(start_ms INTEGER PRIMARY KEY,end_ms INTEGER NOT NULL,kwh REAL NOT NULL)',
            'CREATE TABLE IF NOT EXISTS history_checks(month TEXT PRIMARY KEY,checked_ms INTEGER NOT NULL)',
        ]: system.db.runPrepUpdate(sql,[],DB)
        _ready=True

def record_sample(reading):
    if not reading.get('online') or reading.get('power_w') is None:return
    ensure()
    timestamp=int(reading['updated_ms']);power=cottage_energy.finite(reading['power_w'])
    with _lock:
        tx=system.db.beginTransaction(DB)
        try:
            rows=system.db.runPrepQuery('SELECT ts_ms,power_w FROM power_samples ORDER BY ts_ms DESC LIMIT 1',[],DB,tx=tx)
            if rows and timestamp<=int(rows[0]['ts_ms']):return
            current=dict(ts_ms=timestamp,power_w=power)
            system.db.runPrepUpdate('INSERT INTO power_samples VALUES(?,?,?,?)',
                [timestamp,power,reading.get('voltage_v'),reading.get('current_a')],DB,tx=tx)
            if rows:
                previous=dict(ts_ms=int(rows[0]['ts_ms']),power_w=float(rows[0]['power_w']))
                for minute,kwh,covered in cottage_energy.integrate(previous,current):
                    system.db.runPrepUpdate('INSERT INTO minute_energy VALUES(?,?,?) ON CONFLICT(minute_ms) DO UPDATE SET kwh=kwh+excluded.kwh,covered_ms=covered_ms+excluded.covered_ms',
                        [minute,kwh,covered],DB,tx=tx)
            system.db.commitTransaction(tx)
        except:
            system.db.rollbackTransaction(tx);raise
        finally:system.db.closeTransaction(tx)

def store_intervals(values):
    ensure()
    with _lock:
        tx=system.db.beginTransaction(DB)
        try:
            for a,b,kwh in values:
                overlap=system.db.runPrepQuery('SELECT start_ms,end_ms FROM meter_energy WHERE start_ms<? AND end_ms>? AND NOT(start_ms=? AND end_ms=?)',
                    [b,a,a,b],DB,tx=tx)
                if overlap:raise ValueError('Meter interval overlaps an existing record')
                system.db.runPrepUpdate('INSERT INTO meter_energy VALUES(?,?,?) ON CONFLICT(start_ms) DO UPDATE SET end_ms=excluded.end_ms,kwh=excluded.kwh',
                    [a,b,kwh],DB,tx=tx)
            system.db.commitTransaction(tx)
        except:
            system.db.rollbackTransaction(tx);raise
        finally:system.db.closeTransaction(tx)

def _aggregate(now,monthly):
    first=cottage_energy.months(now)[0]['start'] if monthly else cottage_energy.day_start(now)-6*cottage_energy.DAY
    period="strftime('%Y-%m',start_ms/1000,'unixepoch','+2 hours')" if monthly else "date(start_ms/1000,'unixepoch','+2 hours')"
    sql='''WITH combined AS (
      SELECT minute_ms AS start_ms,kwh,covered_ms,covered_ms AS estimated_ms FROM minute_energy b
      WHERE minute_ms>=? AND minute_ms<=? AND NOT EXISTS(
        SELECT 1 FROM meter_energy m WHERE m.start_ms<=b.minute_ms AND m.end_ms>=b.minute_ms+60000)
      UNION ALL SELECT start_ms,kwh,end_ms-start_ms AS covered_ms,0 AS estimated_ms FROM meter_energy WHERE start_ms>=? AND end_ms<=?
    ) SELECT '''+period+''' AS period,SUM(kwh) AS kwh,SUM(covered_ms) AS covered_ms,SUM(estimated_ms) AS estimated_ms
      FROM combined GROUP BY period ORDER BY period'''
    return system.db.runPrepQuery(sql,[first,now,first,now],DB)

def snapshot(now,reading):
    ensure()
    with _lock:
        if now-_cache.get('at',0)>10000:
            rows=system.db.runPrepQuery('SELECT (ts_ms/60000)*60000 AS minute_ms,AVG(power_w)/1000.0 AS power_kw FROM power_samples WHERE ts_ms>=? AND ts_ms<=? GROUP BY minute_ms ORDER BY minute_ms',
                [now-cottage_energy.DAY,now],DB)
            _cache.update(at=now,profile={int(r['minute_ms']):float(r['power_kw']) for r in rows},
                daily=cottage_energy.bars(_aggregate(now,False),now),monthly=cottage_energy.bars(_aggregate(now,True),now,True))
            first=system.db.runPrepQuery('SELECT MIN(ts_ms) AS first_ms FROM power_samples',[],DB)
            _cache['first_ms']=int(first[0]['first_ms']) if first and first[0]['first_ms'] is not None else None
        minute=(now//60000)*60000
        profile=[dict(time=minute-cottage_energy.DAY+i*60000,power_kw=_cache['profile'].get(minute-cottage_energy.DAY+i*60000)) for i in range(1441)]
        live=[]
        if reading.get('online') and now-int(reading.get('updated_ms',0))<=15000:
            live=[dict(time=int(reading['updated_ms']),power_kw=reading['power_kw'])]
        state=system.util.getGlobals().get(KEY,{})
        result=dict(profile=profile,live=live,daily=_cache['daily'],monthly=_cache['monthly'],first_ms=_cache.get('first_ms'),
            meter_history_status=state.get('status','Checking meter history'),sample_history_configured=True)
    return result

def _backfill():
    state=system.util.getGlobals()[KEY]
    time.sleep(4)
    while state.get('owner') is _owner:
        try:
            ensure();now=system.date.toMillis(system.date.now())
            for period in reversed(cottage_energy.months(now)):
                if state.get('owner') is not _owner:return
                rows=system.db.runPrepQuery('SELECT checked_ms FROM history_checks WHERE month=?',[period['key']],DB)
                cooldown=900000 if now<period['end'] else 86400000
                if rows and now-int(rows[0]['checked_ms'])<cooldown:continue
                system.db.runPrepUpdate('INSERT INTO history_checks VALUES(?,?) ON CONFLICT(month) DO UPDATE SET checked_ms=excluded.checked_ms',[period['key'],now],DB)
                end=min(now,period['end'])
                state['status']='Reading meter energy records'
                records,resolution=cube_meter.query_consumption(period['start'],end)
                accepted=cottage_energy.intervals(records,period['start'],end,resolution)
                store_intervals(accepted)
                state['status']='Meter energy records imported' if accepted else 'Earlier meter records unavailable; collecting live history'
                state['last_import_count']=len(accepted)
                state['total_imported']=state.get('total_imported',0)+len(accepted)
                time.sleep(8)
        except:
            kind=getattr(sys.exc_info()[0],'__name__','HistoryError')
            state['status']='Earlier meter history unavailable ('+kind+'); collecting live history'
        time.sleep(60)

def start():
    values=system.util.getGlobals()
    with _lock:
        state=values.setdefault(KEY,{})
        if state.get('owner') is _owner:return
        state['owner']=_owner
        worker=threading.Thread(target=_backfill,name='Cottage-energy-history-query')
        worker.setDaemon(True);worker.start()
