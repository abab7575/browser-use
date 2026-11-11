"""Phase 0: intersect lidar coverage with Tipperary; summarise by survey/resolution; draw a coverage map."""
import json, pathlib, collections
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely import STRtree
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
C = pathlib.Path(__file__).resolve().parent.parent / 'cache'
tipp = unary_union([shape(f['geometry']) for f in json.load(open(C / 'tipperary_boundary.geojson'))['features']])
smr = [(f['properties']['ITM_E'], f['properties']['ITM_N'], f['properties']['MONUMENT_CLASS']) for f in json.load(open(C / 'smr_tipperary.geojson'))['features'] if f['properties']['ITM_E'] and f['properties']['ITM_E'] > 1000]
print(f'Tipperary area {tipp.area/1e6:.0f} km2, SMR records {len(smr)}')
fig, ax = plt.subplots(figsize=(11, 13))
for g in getattr(tipp, 'geoms', [tipp]): ax.plot(*g.exterior.xy, 'k', lw=1)
cols = {1.0: 'tab:green', 2.0: 'tab:orange'}
out = []
for p in sorted((C / 'coverage').glob('*.geojson')):
	keep = collections.defaultdict(list)
	for f in json.load(open(p))['features']:
		g = shape(f['geometry'])
		if g.intersects(tipp):
			a = f['properties']; keep[a.get('RESOLUTION')].append(g)
			out.append({'survey': p.stem, 'res': a.get('RESOLUTION'), 'name': a.get('DATA_NAME'), 'url': a.get('DATA_URL'), 'date': a.get('DATECAPTUR'), 'bounds': g.bounds, 'licence': a.get('LICENCE')})
	for res, gs in keep.items():
		u = unary_union(gs).intersection(tipp)
		print(f'{p.stem:14s} res={res}m tiles={len(gs):4d} area_in_tipp={u.area/1e6:7.1f} km2')
		for g in gs:
			ax.fill(*g.exterior.xy, color=cols.get(res, 'tab:red' if (res or 9) > 2 else 'tab:blue'), alpha=.45, lw=0)
json.dump(out, open(C / 'tipperary_tiles.json', 'w'))
ax.scatter([s[0] for s in smr], [s[1] for s in smr], s=.4, c='tab:blue', alpha=.35)
from pyproj import Transformer
tr = Transformer.from_crs(4326, 2157, always_xy=True)
TOWNS = {'Nenagh': (52.862, -8.197), 'Thurles': (52.679, -7.814), 'Clonmel': (52.355, -7.704), 'Cashel': (52.516, -7.889), 'Tipperary': (52.474, -8.162), 'Cahir': (52.375, -7.925), 'Roscrea': (52.955, -7.798), 'Carrick-on-Suir': (52.346, -7.413), 'Templemore': (52.795, -7.833), 'Fethard': (52.467, -7.692), 'Borrisokane': (52.997, -8.127), 'Newport': (52.709, -8.409)}
for n, (la, lo) in TOWNS.items():
	x, y = tr.transform(lo, la); ax.plot(x, y, 'r^', ms=6); ax.annotate(n, (x, y), fontsize=10, color='darkred', xytext=(4, 4), textcoords='offset points', weight='bold')
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title('Tipperary lidar coverage (orange = 2m DTM (only resolution available); blue dots = SMR monuments')
fig.savefig(C.parent / 'phase0_coverage.png', dpi=110, bbox_inches='tight')
