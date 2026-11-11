"""Phase 0: cache Tipperary boundary (Tailte Eireann) and Tipperary SMR records (NMS). Rate-limited, cached."""
import json, time, urllib.request, urllib.parse, pathlib
C = pathlib.Path(__file__).resolve().parent.parent / 'cache'
def get(url):
	time.sleep(1.0)
	return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'lidar-research-script'}), timeout=180))
CO = 'https://services-eu1.arcgis.com/FH5XCsx8rYXqnjF5/arcgis/rest/services/Counties___OSi_National_Statutory_Boundaries___Generalised_20m/FeatureServer/0/query?'
f = C / 'tipperary_boundary.geojson'
if not f.exists():
	d = get(CO + urllib.parse.urlencode({'where': "ENGLISH='TIPPERARY'", 'outFields': 'ENGLISH', 'outSR': 2157, 'f': 'geojson'}))
	f.write_text(json.dumps(d)); print('boundary', len(d['features']))
SMR = 'https://services-eu1.arcgis.com/HyjXgkV6KGMSF3jt/arcgis/rest/services/SMROpenData/FeatureServer/0/query?'
f = C / 'smr_tipperary.geojson'
if not f.exists():
	feats, off = [], 0
	while True:
		d = get(SMR + urllib.parse.urlencode({'where': "COUNTY LIKE 'TIPP%'", 'outFields': 'ENTITY_ID,SMRS,COUNTY,TOWNLAND,ITM_E,ITM_N,LONGITUDE,LATITUDE,MONUMENT_CLASS,CLASS_CODE,WEBSITE_LINK', 'outSR': 2157, 'f': 'geojson', 'resultOffset': off, 'resultRecordCount': 2000, 'orderByFields': 'OBJECTID'}))
		feats += d['features']; off += len(d['features'])
		if len(d['features']) < 2000: break
	f.write_text(json.dumps({'type': 'FeatureCollection', 'features': feats})); print('smr', len(feats))
