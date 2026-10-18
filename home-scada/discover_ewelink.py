"""Read-only, bounded DNS-SD discovery; no device commands or encrypted data saved."""
import datetime,json,socket,struct,time
from pathlib import Path

SERVICE='_ewelink._tcp.local'
LOCAL_IP='192.168.68.179'

def name(packet,pos):
    labels=[]; end=None; seen=set()
    for _ in range(100):
        if pos in seen: raise ValueError('DNS compression loop')
        seen.add(pos); n=packet[pos]
        if n&0xc0==0xc0:
            if end is None: end=pos+2
            pos=((n&0x3f)<<8)|packet[pos+1]; continue
        pos+=1
        if n==0: return '.'.join(labels),end or pos
        labels.append(packet[pos:pos+n].decode('utf-8',errors='replace')); pos+=n
    raise ValueError('DNS name too long')

def query(value,kind=12):
    encoded=b''.join(bytes([len(p)])+p.encode() for p in value.split('.'))+b'\0'
    return struct.pack('!HHHHHH',0,0,1,0,0,0)+encoded+struct.pack('!HH',kind,0x8001)

def records(packet):
    _,_,questions,answers,authorities,additional=struct.unpack('!6H',packet[:12]); pos=12
    for _ in range(questions): _,pos=name(packet,pos); pos+=4
    result=[]
    for _ in range(answers+authorities+additional):
        owner,pos=name(packet,pos); kind,cls,ttl,length=struct.unpack('!HHIH',packet[pos:pos+10]); pos+=10
        end=pos+length; value=None
        if kind==1 and length==4: value=socket.inet_ntoa(packet[pos:end])
        elif kind==12: value=name(packet,pos)[0]
        elif kind==33: value=dict(port=struct.unpack('!H',packet[pos+4:pos+6])[0],host=name(packet,pos+6)[0])
        elif kind==16:
            value={}; p=pos
            while p<end:
                n=packet[p]; p+=1; item=packet[p:p+n].decode('utf-8',errors='replace'); p+=n
                key,sep,val=item.partition('=')
                if key.lower() in ('id','deviceid','type','apivers','encrypt'): value[key]=val
        if value is not None: result.append((owner,kind,value))
        pos=end
    return result

def main():
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((LOCAL_IP,0)); sock.settimeout(.5)
    sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_IF,socket.inet_aton(LOCAL_IP))
    sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,255)
    discovered={}; addresses={}; queried=set(); deadline=time.monotonic()+7
    sock.sendto(query(SERVICE),('224.0.0.251',5353))
    while time.monotonic()<deadline:
        try: packet,sender=sock.recvfrom(65535)
        except socket.timeout: continue
        try: rr=records(packet)
        except (ValueError,IndexError,struct.error): continue
        for owner,kind,value in rr:
            if kind==1: addresses[owner]=value
            if kind==12 and owner.lower()==SERVICE:
                discovered.setdefault(value,{})
                if value not in queried:
                    sock.sendto(query(value,255),('224.0.0.251',5353)); queried.add(value)
            if owner.lower().endswith('.'+SERVICE):
                d=discovered.setdefault(owner,{}); d['response_ip']=sender[0]
                if kind==33: d.update(value)
                elif kind==16: d['metadata']=value
    sock.close()
    devices=[dict(service=n,**d,ip=addresses.get(d.get('host',''),d.get('response_ip'))) for n,d in discovered.items()]
    report=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),interface_ip=LOCAL_IP,method='DNS-SD PTR query only',devices=devices,commands_sent=False,keys_or_encrypted_payload_saved=False,note='No response does not establish that the meter is offline; LAN setting, Wi-Fi isolation and firewall may prevent discovery.')
    (Path(__file__).resolve().parent/'qa/ewelink-discovery.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

if __name__=='__main__': main()
