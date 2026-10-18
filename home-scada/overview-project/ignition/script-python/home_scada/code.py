"""One quiet cottage overview backed only by real live readings and persisted history."""
import time

def snapshot():
    now=system.date.toMillis(system.date.now())
    reading=cube_meter.snapshot()
    try:
        cottage_history.start()
        history=cottage_history.snapshot(now,reading)
        note='Energy includes estimates from recorded power when meter totals are unavailable. Gaps are excluded; today and this month are in progress.'
        if history.get('first_ms'):
            note='Live history since '+system.date.format(system.date.fromMillis(history['first_ms']),'dd MMM yyyy HH:mm')+'. '+note
    except:
        history=dict(profile=[],live=[],daily=[],monthly=[],first_ms=None,meter_history_status='History storage starting',sample_history_configured=False)
        note='History storage is starting. Live readings remain available.'
    result=dict(cottage=reading,history=history,range_start=now-86400000,range_end=now,history_note=note,
        connection='Live' if reading.get('online') else 'Meter unavailable',physical_commands_enabled=False)
    try:
        evidence=dict(online=reading.get('online'),updated_ms=reading.get('updated_ms'),power_kw=reading.get('power_kw'),
            history_configured=history['sample_history_configured'],profile_points=sum(p.get('power_kw') is not None for p in history['profile']),
            daily=history['daily'],monthly=history['monthly'],history_status=history['meter_history_status'],note=note)
        system.file.writeFile('C:/Users/Paul/OneDrive/Desktop/Ignition/home-scada/qa/overview-runtime.json',system.util.jsonEncode(evidence))
    except:pass
    return result
