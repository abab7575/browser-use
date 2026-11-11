"""Phase 0: measure real data fill in each DTM tile (100 m cells), map it, and rank ~100 km2 blocks by usable area."""
import json, pathlib, glob, numpy as np, rasterio
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from shapely import prepared
from pyproj import Transformer
R = pathlib.Path(__file__).resolve().parent.parent; C = R / 'cache'
X0, Y0, X1, Y1, CELL = 560000, 600000, 650000, 716000, 100
W, H = (X1 - X0) // CELL, (Y1 - Y0) // CELL
cov = np.zeros((H, W), 'float32')  # fraction of each 100 m cell with valid DTM
for p in sorted(glob.glob(str(C / 'dtm' / '*.tif'))):
	with rasterio.open(p) as r:
		a = r.read(1); b = r.bounds
	v = np.isfinite(a) & (a > -50) & (a < 2000)
	if r.nodata is not None: v &= a != r.nodata
	n = int(round(CELL / r.res[0]))
	hh, ww = (a.shape[0] // n) * n, (a.shape[1] // n) * n
	f = v[:hh, :ww].reshape(hh // n, n, ww // n, n).mean((1, 3))
	c0, r0 = int(round((b.left - X0) / CELL)), int(round((Y1 - b.top) / CELL))
	sub = cov[r0:r0 + f.shape[0], c0:c0 + f.shape[1]]
	np.maximum(sub, f[:sub.shape[0], :sub.shape[1]], out=sub)
np.save(C / 'coverage_100m.npy', cov)
tipp = unary_union([shape(f['geometry']) for f in json.load(open(C / 'tipperary_boundary.geojson'))['features']])
pt = prepared.prep(tipp)
inside = np.array([[pt.contains(Point(X0 + (c + .5) * CELL, Y1 - (r + .5) * CELL)) for c in range(W)] for r in range(H)])
covt = cov * inside
print(f'Real 2 m DTM coverage inside Tipperary: {covt.sum() * CELL * CELL / 1e6:.0f} km2 of {tipp.area / 1e6:.0f} km2')
smr = np.array([(f['properties']['ITM_E'], f['properties']['ITM_N']) for f in json.load(open(C / 'smr_tipperary.geojson'))['features'] if (f['properties']['ITM_E'] or 0) > 1000])
sc = ((smr[:, 0] - X0) // CELL).astype(int); sr = ((Y1 - smr[:, 1]) // CELL).astype(int)
ok = (sc >= 0) & (sc < W) & (sr >= 0) & (sr < H)
smr_cov = np.zeros((H, W)); np.add.at(smr_cov, (sr[ok], sc[ok]), cov[sr[ok], sc[ok]] > .5)
print('SMR records sitting on covered ground:', int(smr_cov.sum()))
# sliding window: BLOCK km square, step 1 km
def windows(bk):
	n = bk * 1000 // CELL; out = []
	ci = np.pad(covt, 1).cumsum(0).cumsum(1)[1:, 1:]; si = smr_cov.cumsum(0).cumsum(1)
	def box(I, r, c): return I[r + n - 1, c + n - 1] - (I[r - 1, c + n - 1] if r else 0) - (I[r + n - 1, c - 1] if c else 0) + (I[r - 1, c - 1] if r and c else 0)
	ci = covt.cumsum(0).cumsum(1)
	for r in range(0, H - n, 10):
		for c in range(0, W - n, 10):
			out.append((float(box(ci, r, c)) * CELL * CELL / 1e6, int(box(si, r, c)), X0 + c * CELL, Y1 - (r + n) * CELL))
	return sorted(out, reverse=True)
res = {}
for bk in (10, 14):
	ws = windows(bk); picked = []
	for w in ws:  # non-overlapping top picks
		if all(abs(w[2] - q[2]) >= bk * 1000 or abs(w[3] - q[3]) >= bk * 1000 for q in picked): picked.append(w)
		if len(picked) == 8: break
	res[bk] = picked
	print(f'\nBest {bk}x{bk} km blocks (covered km2, SMR on covered ground, SW corner ITM):')
	for w in picked: print(f'  {w[0]:6.1f} km2  smr={w[1]:4d}  E{w[2]} N{w[3]}')
json.dump(res, open(C / 'block_ranking.json', 'w'))
fig, ax = plt.subplots(figsize=(10, 12.5))
ax.imshow(np.where(covt > 0, covt, np.nan), extent=(X0, X1, Y0, Y1), cmap='Oranges', vmin=0, vmax=1.3)
for g in getattr(tipp, 'geoms', [tipp]): ax.plot(*g.exterior.xy, 'k', lw=1)
ax.scatter(smr[:, 0], smr[:, 1], s=.4, c='tab:blue', alpha=.3)
tr = Transformer.from_crs(4326, 2157, always_xy=True)
TOWNS = {'Nenagh': (52.862, -8.197), 'Thurles': (52.679, -7.814), 'Clonmel': (52.355, -7.704), 'Cashel': (52.516, -7.889), 'Tipperary': (52.474, -8.162), 'Cahir': (52.375, -7.925), 'Roscrea': (52.955, -7.798), 'Carrick-on-Suir': (52.346, -7.413), 'Templemore': (52.795, -7.833), 'Fethard': (52.467, -7.692), 'Borrisokane': (52.997, -8.127), 'Newport': (52.709, -8.409)}
for nm, (la, lo) in TOWNS.items():
	x, y = tr.transform(lo, la); ax.plot(x, y, 'r^', ms=6); ax.annotate(nm, (x, y), fontsize=10, color='darkred', weight='bold', xytext=(4, 4), textcoords='offset points')
for i, w in enumerate(res[10][:5]):
	ax.add_patch(plt.Rectangle((w[2], w[3]), 10000, 10000, fill=False, ec='green', lw=2)); ax.text(w[2] + 300, w[3] + 300, f'{chr(65 + i)}: {w[0]:.0f} km2', color='green', weight='bold')
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.grid(alpha=.3)
ax.set_title('Co. Tipperary: actual 2 m lidar DTM coverage (orange), SMR monuments (blue),\nbest-covered 10x10 km squares (green)')
fig.savefig(R / 'phase0_coverage.png', dpi=110, bbox_inches='tight')
