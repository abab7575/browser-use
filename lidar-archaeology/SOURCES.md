# Data sources

Checked 2026-11-11. Every source below was tested from a script, not assumed.

## 1. Lidar terrain models (DTM) — WORKS, but 2 m only in Tipperary
- Publisher: Geological Survey Ireland (GSI), Open Topographic Data Viewer.
- Listing: https://data.gov.ie/dataset/open-topographic-lidar-data
- Tile index (footprints + download link per tile): `https://gsi.geodata.gov.ie/server/rest/services/Lidar/IE_GSI_LiDAR_Coverage_<survey>_IE26_ITM/FeatureServer`
- Tile downloads: `https://gsi.geodata.gov.ie/downloads/LIDAR/...zip` (GeoTIFF, EPSG:2157, 2 km x 2 km tiles).
- Surveys covering Co. Tipperary (both 2 m; no 1 m or better exists in the open data for this county):
  - TII (Transport Infrastructure Ireland), flown May 2010 – May 2011, 206 tiles, road corridors.
  - OPW / NASC (Office of Public Works), flown 2011, 88 tiles, river flood corridors. DTM and DSM in each zip; we use the DTM only.
- Licence: CC BY 4.0.
- Attribution (TII tiles): "Contains Irish Public Sector Data (Geological Survey Ireland & Transport Infrastructure Ireland) licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) licence."
- Attribution (OPW tiles): as stated in the `Copyright_and_Licence.txt` inside each zip (Office of Public Works, CC BY 4.0).
- Note: `https://gsi.geodata.gov.ie/imagehost/rest/services/Lidar` serves pre-rendered 8-bit hillshade pictures, not elevation. Not used for analysis.

## 2. Known monuments (SMR) — WORKS
- Publisher: National Monuments Service, Dept. of Housing, Local Government and Heritage. "Archaeological Survey of Ireland" dataset.
- Listing: https://data.gov.ie/dataset/national-monuments-service-archaeological-survey-of-ireland
- Service used: https://services-eu1.arcgis.com/HyjXgkV6KGMSF3jt/arcgis/rest/services/SMROpenData/FeatureServer/0 (151,308 records nationally; 9,258 for Tipperary North + South).
- Licence: CC BY 4.0. Attribution: National Monuments Service, Government of Ireland.
- Caveat: the open SMR is not the complete record. It excludes some unpublished/pending records, and separate datasets exist (e.g. NIAH, excavation database). "Not in the SMR" does not mean "unknown to NMS".

## 3. County boundary — WORKS
- Tailte Éireann, "Counties - National Statutory Boundaries - 2019 - Generalised 20m". CC BY 4.0.
- https://services-eu1.arcgis.com/FH5XCsx8rYXqnjF5/arcgis/rest/services/Counties___OSi_National_Statutory_Boundaries___Generalised_20m/FeatureServer
- Townland boundaries (for naming candidates): Tailte Éireann "Townlands - National Statutory Boundaries - Ungeneralised 2026", same host, CC BY 4.0.

## 4. Historic 6-inch / 25-inch maps — NOT AVAILABLE to scripts
- Tailte Éireann MapGenie historic layers (6-inch first/last edition, 25-inch) exist only as licensed services behind the "Irish Townland and Historical Map Viewer". Direct requests return HTTP 403 (permission denied). They are not open data, and we have not tried to get around the restriction.
- Manual route (free, in a browser): https://experience.arcgis.com/experience/bdc13f643b68486c99e23abdaed0a98e — or the NMS Historic Environment Viewer https://maps.archaeology.ie/historicenvironment
- Consequence: the historic-map check in Phase 4 must be done by a person for the final shortlist, unless a licence/API key is obtained.

## 5. Modern aerial imagery — PARTIAL
- No openly licensed high-resolution aerial imagery of Ireland was found. Tailte Éireann imagery is behind the same 403.
- Esri World Imagery: reachable without a key (`https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer`). NOT an open licence; Esri terms allow viewing/internal use with attribution ("Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"). Not for redistribution. Use needs owner's sign-off.
- Sentinel-2 (Copernicus, open licence) is 10 m per pixel: too coarse to tell a slurry tank from a ringfort. Not useful here.
- OpenStreetMap (ODbL) could help flag modern features, but the Overpass API was not reachable from this environment.
