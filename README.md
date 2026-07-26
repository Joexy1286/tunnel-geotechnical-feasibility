# Geological-Geotechnical Feasibility Study
## Tunnel Alignment: Kornelimünster → Walheim → Friesenrath
### Aachen Region, North Rhine-Westphalia, Germany

**Joexy1286**  
Field Tunnel Mapping Training | Geological-Geotechnical Cross Section & Site Investigation Programme  
[LinkedIn](https://linkedin.com/in/joseph-turkson) · [Reservoir Geology Portfolio](https://github.com/Joexy1286/reservoir-geology-portfolio) · [CO₂ Mineralisation Portfolio](https://github.com/Joexy1286/co2-mineralisation-phreeqc)

---

## Project Overview

This repository presents a **feasibility-level geological-geotechnical study** of a proposed ~4.3 km tunnel alignment running from Kornelimünster through Walheim to Friesenrath in the Aachen region of NRW, Germany. The study was conducted as part of a Field Tunnel Mapping Training exercise and follows standard engineering geological feasibility methodology.

The alignment traverses a complex sequence of **Devonian and Carboniferous formations** including carbonate units with significant karst potential, a major thrust fault (Breinigerberg Überschiebung), and zones of shallow bedrock cover — all presenting distinct geotechnical challenges for tunnel design and construction.

---

## Methodology

### Data Sources
| Dataset | Source | Format |
|---|---|---|
| Geological map (1:50,000) | IS GK50 WMS — GeoPortal NRW | WMS / Shapefile |
| Digital Terrain Model (DGM1, 1m) | Geobasis NRW | GeoTIFF tiles |
| Fault structures | IS GK50 — Störungen layer | Shapefile |
| Coordinate system | EPSG:25832 (ETRS89 / UTM zone 32N) | — |

### Workflow
```
1. QGIS project setup — EPSG:25832, WMS basemap, GK50 geological layers
         │
         ▼
2. Tunnel alignment digitisation — 4.28 km polyline, 500 m corridor buffer
         │
         ▼
3. DEM processing — DGM1 tile mosaic → Virtual Raster → surface profile extraction
         │
         ▼
4. Bedrock surface — Quaternary-base contours → TIN interpolation → bedrock-top profile
         │
         ▼
5. Points Along Geometry (10 m spacing) → Sample Raster Values → Join Attributes
   (surface elevation, bedrock top, overburden, GK50 lithology attributes)
         │
         ▼
6. Python cross section generation — matplotlib, 8 formations, hazard zonation
         │
         ▼
7. Hazard assessment — karst, groundwater ingress, fault zone, shallow cover
         │
         ▼
8. Site investigation programme — geophysics-first, targeted borehole clusters
```

---

## Key Findings

### Alignment Statistics
| Parameter | Value |
|---|---|
| Total alignment length | 4,280 m |
| Surface elevation range | 229.9 – 307.9 m asl |
| Bedrock surface range | 224.3 – 294.1 m asl |
| Overburden range | 0 – 46 m |
| Points with < 20 m cover | 274 / 429 (64%) |
| TIN edge anomalies flagged | 23 points |
| Fault crossing | Breinigerberg Überschiebung (~Ch. 1800, ~38 m lateral offset) |

### Formation Summary
| Formation | Chainage (m) | Mean Cover (m) | Hazard |
|---|---|---|---|
| Hastière/Pont d'Arcole/Vesdre-Fm. (Mittlerer Kohlenkalk) | 0–690 | 11.2 | ⛔ Very High |
| Terwagne/Neffe-Fm. (Oberer Kohlenkalk) | 700–1100 | 8.4 | ⛔ Very High |
| Esneux/Evieux-Fm. (Condroz-Sandstein) | 1110–2670 | 31.6 | ✅ Low |
| Schmidthof-Fm. + Famenne Schiefer | 2680–3260 | 17.2 | ⚠️ Moderate |
| Schmidthof-Fm., Frasnes-Knollenkalk | 3270–3600 | 17.4 | 🔴 High |
| Friesenrath-Formation | 3610–3780 | 1.3 | ✅ Low |
| Massenkalk (ungegliedert) | 3790–3860 | 6.3 | 🔴 High |
| Fleuth-Schichten | 3870–4280 | 8.0 | ✅ Low |

---

## Figures

### Figure 1 — Geological-Geotechnical Cross Section
*Main deliverable — 3-panel display: geological section · overburden profile · hazard strip*

![Geological cross section](figures/01_geological_cross_section.png)

**Reading the section:**
- **Upper panel:** Colour-coded lithological units from GK50, Quaternary cover (tan), bedrock surface (dashed gold), and tunnel envelope (blue). The Breinigerberg Überschiebung fault zone is shown in red at Ch. ~1800.
- **Middle panel:** Rock cover above tunnel crown. Gold dashed line = 20 m minimum cover threshold. Red areas indicate negative overburden (TIN edge effects — require field verification).
- **Lower panel:** Hazard zonation strip colour-coded by geotechnical risk level — green (low) through dark red (very high). Carbonate units at Ch. 0–1100 represent the highest-risk section.

---

### Figure 2 — Formation Statistics & Geotechnical Summary
*Formation distribution, overburden histogram, hazard pie chart*

![Formation statistics](figures/02_formation_statistics.png)

Key observations:
- The Esneux-Evieux Formation (Condroz-Sandstein) dominates the central section (Ch. 1110–2670) and represents the most favourable ground — competent sandstone, adequate cover, low karst risk.
- Carbonate formations (cvtene, ctmk) account for ~26% of the alignment length but carry the highest geotechnical risk due to karst dissolution potential.
- 64% of alignment points fall below the 20 m minimum cover threshold — largely in the carbonate-dominated northern section.

---

### Figure 3 — Site Investigation Programme
*Geophysics-first strategy with targeted borehole clusters at high-risk zones*

![Site investigation](figures/03_site_investigation.png)

**Investigation strategy:**
- **Phase 1 (Geophysics):** Full-alignment 2D ERT and seismic refraction profile to map bedrock depth, fault zone geometry, and karst cavities without drilling.
- **Phase 2 (Boreholes):** Seven targeted boreholes at key risk zones (portals, fault zone, karst sections, shallow cover concentrations).
- **Phase 3 (Monitoring):** Standpipe piezometers in BH-2, BH-3, and BH-6 for 6-month groundwater baseline prior to construction.

---

## Hazard Assessment Summary

| Hazard | Risk Level | Location | Recommended Mitigation |
|---|---|---|---|
| Karst / dissolution features | Very High | Ch. 0–1100 (carbonates) | Pre-excavation grouting; probe drilling ahead of face |
| Groundwater ingress | High | Ch. 0–1100, Ch. 3790–3860 | Groundwater baseline monitoring; NATM with drainage |
| Fault zone crossing | High | Ch. ~1800 (Breinigerberg Überschiebung) | Reduced advance rate; temporary support; pre-grouting |
| Shallow rock cover | Moderate–High | Multiple zones (64% of alignment) | Settlement monitoring; compensatory grouting where < 10 m |
| Lithological heterogeneity | Moderate | Transitions at Ch. ~1100, ~2670, ~3600 | Adaptable support class; face mapping during excavation |

---

## Repository Structure

```
tunnel-geotechnical-feasibility/
├── README.md
├── figures/
│   ├── 01_geological_cross_section.png   # Main 3-panel cross section
│   ├── 02_formation_statistics.png        # Formation stats & hazard summary
│   └── 03_site_investigation.png          # Site investigation programme
├── scripts/
│   └── build_cross_section.py            # Full Python workflow
└── data/
    └── profile_points_v2_lithology_v2.csv  # QGIS-exported point dataset
```

---

## Dependencies

```bash
pip install numpy pandas matplotlib scipy
```

---

## Connection to Other Work

This engineering geology project complements the subsurface characterisation skills demonstrated in my other portfolio repositories:

- **[reservoir-geology-portfolio](https://github.com/Joexy1286/reservoir-geology-portfolio)** — petrophysical well log analysis, CCS storage assessment (Norwegian North Sea analogue)
- **[co2-mineralisation-phreeqc](https://github.com/Joexy1286/co2-mineralisation-phreeqc)** — PHREEQC reactive transport modelling of CO₂ mineralisation in basalt systems

Together these three repositories demonstrate a complete range of applied geoscience skills spanning engineering geology, reservoir characterisation, and geochemical modelling.

---

*Geological data: IS GK50 © Geologischer Dienst NRW. Terrain data: DGM1 © Geobasis NRW. Academic use only.*
