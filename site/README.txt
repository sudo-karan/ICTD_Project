ODISHA FOREST DECISION LAYER
A working map for discussion. Online at https://sudo-karan.github.io/ICTD_Project/

HOW TO OPEN IT
Open the address above in a web browser. Or keep index.html and data.js together in one folder
and open index.html (double-click it): it needs nothing installed and works without a
connection. Once it has loaded, the page asks no other site for anything. We've checked the map
in Chrome and in Safari's engine (WebKit) on a laptop, and this copy in Chrome; it's laid out
for a laptop, and in a window as narrow as a phone's the map gets no room between the two side
panels, so it won't work on a phone yet (we haven't tried one). On the page, "About this map"
explains how it's made and how to read it, and "Sources" says where the data comes from and
under what licence.

WHAT IT SHOWS
11,468 units covering Odisha: panchayat units, and the land outside any revenue village. For
each, it shows forest condition, past MGNREGA spending and social need, each as its own layer,
built from public data. The decision view reads the forest data a second way: each unit goes in
one of six cells, by how much of its forest of 2000 has no loss recorded since (10 ha or more,
or less) and by the forest loss recorded in a window of years you choose (1 ha or more, or
less). Within one district, units are listed tier by tier.
  The six cells:
    Closed forest, little or no loss recorded - protect
    Closed forest, loss recorded - find the cause first
    Open forest, little or no loss recorded - assisted natural regeneration candidate
    Open forest, loss recorded - restore
    Little forest left, loss recorded - verify on the ground
    Not a forest site

WHAT IT ISN'T
- Not a verdict on any place, and not a score. It's a starting point for where to look, to be
  checked against what people who know the places see.
- Standing forest here is the forest of 2000 with no loss recorded since; not a measure of tree
  cover today. The page quotes the data provider's own cautions.
- The order of the tiers is provisional, to be set with the Foundation for Ecological Security:
  1 Open forest, loss recorded - restore; 2 Closed forest, loss recorded - find the cause first;
  3 Open forest, little or no loss recorded - assisted natural regeneration candidate; 4 Closed
  forest, little or no loss recorded - protect; 5 Little forest left, loss recorded - verify on
  the ground. You can change it on the page.
- Which works from the official list fit which cell is our proposal, not a ruling.
- A unit is a shape on a map, not a jurisdiction; the census figures are from 2011; the
  geotagged record of works effectively ends in 2017-18.

LEFT OUT OF THIS COPY
- The loss-pixel overlay. The full version can lay Hansen's loss over the map as tiles from an
  outside provider's server. We've left it out while two points of that provider's terms of use
  are unresolved; its box on the page is greyed out.
- The development index is not in this copy. The full version also shows a 2011 village
  development index ('Aggregate Development Index 2011') as a layer, as a line in each unit's
  panel and as a column of the list. No file we share carries it.
Apart from these two, this copy's two files are the full version's own.

CREDITS AND LICENCES (the rows of the page's "Sources")
- Tree canopy in 2000 and tree cover loss 2001-2025: Hansen, Potapov, Moore, Hancher et al.,
Global Forest Change v1.13 (University of Maryland), through Google Earth Engine; the state's
canopy of 2000 and its loss for 2001-2020 reconciled to Global Forest Watch's published figures,
which stop at 2020. Licence or terms: CC BY 4.0
- Forest cover of Odisha, as a comparison only (no figure of it is on the map): Forest Survey of
India, India State of Forest Report 2023. Licence or terms: © Forest Survey of India; non-
commercial use with acknowledgment
- Tree cover change 2017-2023 (Deforestation, Degradation, No Change, Improvement,
Afforestation, Partially Degraded): CoRE Stack (Commoning for Resilience and Equality), ACT4D
group, IIT Delhi - core-stack.org. Licence or terms: CC BY 4.0
- Population, households, Scheduled Tribe and Scheduled Caste population: Census of India 2011,
village rows as compiled by the ICTD group, IIT Delhi. Licence or terms: Government of India;
compilation CC BY 4.0
- MGNREGA works and expenditure: Ministry of Rural Development: geotagged assets (Bhuvan
GeoMGNREGA), as published by CoRE Stack; MGNREGA MIS report R6.20 for the state-level
statements. Licence or terms: Government of India public data; compilation CC BY 4.0
- Unit boundaries, and district names of the land outside villages: DataMeet Community, Indian
village boundaries (Odisha), joined to LGD panchayat ids. Licence or terms: ODbL 1.0. The shapes
in this file are a database derived from DataMeet's and are offered under the same licence
- Poverty rate (NOT in this file): SHRUG 2.2, Development Data Lab. Licence or terms: CC BY-NC-
SA 4.0. The analysis behind this map uses SHRUG's small-area poverty estimates; no SHRUG-derived
figure is included here, so that this file does not become a derived work under that licence
- The map library: Leaflet 1.9.4. Licence or terms: BSD 2-Clause, © Volodymyr Agafonkin and
CloudMade; embedded unmodified
- Loss-pixel overlay (not in this copy): Global Forest Watch (World Resources Institute): tree
cover loss map tiles, Hansen/UMD Global Forest Change v1.13. Licence or terms: Source:
Hansen/UMD/Google/USGS/NASA. Global Forest Change v1.13, CC BY 4.0. Tiles served by Global
Forest Watch (World Resources Institute). Terms of use: https://globalnaturewatch.org/terms/.
Two points of them are unresolved, which is why the overlay is not in this copy.
- Cautions about Hansen's data quoted in the decision view: Global Forest Watch's record of the
dataset Tree cover loss (https://data-api.globalforestwatch.org/dataset/umd_tree_cover_loss) and
the University of Maryland's page for Global Forest Change version 1.13
(https://storage.googleapis.com/earthenginepartners-hansen/GFC-2025-v1.13/download.html), both
as read on 8 October 2026. Licence or terms: Short quotations, each with its source; the data
itself is CC BY 4.0
- Work types named in the decision view: Ministry of Rural Development notification S.O.
5448(E), 5 October 2026: the list of permissible works under the VB-G RAM G Act (375 works);
Gazette of India, read from egazette.gov.in. Licence or terms: Government of India; no licence
is stated for the Gazette

SHARING IT
We publish this copy at https://sudo-karan.github.io/ICTD_Project/ (since 11 October 2026). Each
source keeps its own licence, listed above; the unit boundaries in data.js are a database
derived from DataMeet's and are under the Open Database Licence (ODbL 1.0).

THIS COPY
Made 2026-10-12T22:01:24Z (UTC) by scripts/07_build_share.py from the layer built 2026-10-12T22:00:54Z: that layer's two files without
the development index, and with the overlay switched off.
  index.html  214,435 bytes  sha256 ec704c2256678f7ee826d9fe336e137bf59641e2bcebffe0b41b5398eb1e809d
  data.js  23,016,170 bytes  sha256 4f4a1ba75c5a762a8abd6ade431b9167eb93face43f860647a391c46eb9e37b6
