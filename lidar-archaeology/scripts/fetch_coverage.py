"""Phase 0: download lidar coverage footprints (all GSI-hosted surveys) to cache. Rate-limited, cached."""
import json, time, urllib.request, urllib.parse, pathlib, sys
B = 'https://gsi.geodata.gov.ie/server/rest/services/Lidar'
OUT = pathlib.Path(__file__).resolve().parent.parent / 'cache' / 'coverage'
SURVEYS = ['GSI_DCHG_DP', 'GSI_Phase2', 'OPW', 'TII', 'OPW_NASC', 'WH_CoCo', 'OPW_Cork', 'NYU_Dublin']
def get(url):
	time.sleep(1.0)
	req = urllib.request.Request(url, headers={'User-Agent': 'lidar-research-script'})
	return json.load(urllib.request.urlopen(req, timeout=120))
for s in SURVEYS:
	f = OUT / f'{s}.geojson'
	if f.exists():
		print(s, 'cached'); continue
	svc = f'{B}/IE_GSI_LiDAR_Coverage_{s}_IE26_ITM/FeatureServer'
	lid = get(svc + '?f=json')['layers'][0]['id']
	feats, off = [], 0
	while True:
		q = urllib.parse.urlencode({'where': '1=1', 'outFields': '*', 'outSR': 2157, 'f': 'geojson', 'resultOffset': off, 'resultRecordCount': 1000})
		d = get(f'{svc}/{lid}/query?{q}')
		feats += d['features']; off += len(d['features'])
		if not d['features'] or not d.get('properties', d).get('exceededTransferLimit'):
			break
	f.write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}))
	print(s, len(feats), 'tiles'); sys.stdout.flush()
