"""Download + unzip DTM tiles listed in cache/tipperary_tiles.json (or names given as args). Cached; 2s between requests."""
import json, time, urllib.request, pathlib, zipfile, sys, datetime
R = pathlib.Path(__file__).resolve().parent.parent
Z, D = R / 'cache' / 'dtm_zip', R / 'cache' / 'dtm'
Z.mkdir(exist_ok=True); D.mkdir(exist_ok=True)
tiles = json.load(open(R / 'cache' / 'tipperary_tiles.json'))
want = set(sys.argv[1:])
for t in tiles:
	if want and t['name'] not in want: continue
	z = Z / t['url'].rsplit('/', 1)[1]
	out = D / f"{t['survey']}__{t['name']}.tif"
	if out.exists(): continue
	if not z.exists():
		time.sleep(2.0)
		try:
			req = urllib.request.Request(t['url'], headers={'User-Agent': 'lidar-research-script'})
			z.write_bytes(urllib.request.urlopen(req, timeout=300).read())
		except Exception as e:
			print(datetime.datetime.now().isoformat(), 'FAIL', t['name'], t['url'], e, flush=True); continue
	with zipfile.ZipFile(z) as zf:
		tifs = [n for n in zf.namelist() if n.lower().endswith('.tif') and 'dsm' not in n.lower()]
		assert len(tifs) == 1, (t['name'], zf.namelist())
		out.write_bytes(zf.read(tifs[0]))
	print(datetime.datetime.now().isoformat(), 'ok', t['survey'], t['name'], z.stat().st_size, flush=True)
