import json, urllib.request, datetime, pathlib, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'site'/'data'; OUT.mkdir(parents=True,exist_ok=True)
URL='https://models.dev/api.json?type=all'
req=urllib.request.Request(URL,headers={'User-Agent':'ObservatorioModelosIA/1.0','Accept':'application/json'})
with urllib.request.urlopen(req,timeout=90) as response:
    raw=json.load(response)
if not isinstance(raw,dict) or not raw: raise ValueError('Catálogo vacío o inválido')
rows=[]
for pid,provider in raw.items():
    if not isinstance(provider,dict):continue
    models=provider.get('models',{})
    if not isinstance(models,dict):continue
    for mid,m in models.items():
        if not isinstance(m,dict):continue
        rows.append({'key':pid+'/'+mid,'id':mid,'provider':provider.get('name') or pid,'provider_id':pid,'name':m.get('name') or mid,'family':m.get('family'),'status':m.get('status') or 'no especificado','type':m.get('type') or 'chat','release_date':m.get('release_date'),'last_updated':m.get('last_updated'),'reasoning':m.get('reasoning'),'tool_call':m.get('tool_call'),'open_weights':m.get('open_weights'),'cost':m.get('cost') or {},'limit':m.get('limit') or {},'modalities':m.get('modalities') or {}})
if len(rows)<50:raise ValueError('Número de modelos anormalmente bajo; se conserva versión anterior')
rows.sort(key=lambda x:x['key'])
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
current=OUT/'models.json'; previous={}
if current.exists():
    try:previous={x['key']:x for x in json.loads(current.read_text(encoding='utf-8'))['models']}
    except (ValueError,KeyError,TypeError):pass
new={x['key']:x for x in rows}
added=sorted(new.keys()-previous.keys()); removed=sorted(previous.keys()-new.keys())
changed=sorted(k for k in new.keys() & previous.keys() if new[k]!=previous[k])
if previous and len(removed)>len(previous)*0.35:raise ValueError('El catálogo ha perdido más del 35% de modelos; revisión necesaria')
current.write_text(json.dumps({'updated_at':now,'source':URL,'count':len(rows),'models':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
historyfile=OUT/'history.json'; history=[]
if historyfile.exists():
    try:history=json.loads(historyfile.read_text(encoding='utf-8'))
    except ValueError:pass
history.insert(0,{'at':now,'total':len(rows),'added':added,'removed':removed,'changed':changed})
historyfile.write_text(json.dumps(history[:180],ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(f'Modelos: {len(rows)}; altas: {len(added)}; bajas: {len(removed)}; cambios: {len(changed)}')
