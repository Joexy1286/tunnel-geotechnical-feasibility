"""
=============================================================================
GEOLOGICAL-GEOTECHNICAL CROSS SECTION
Tunnel Alignment: Kornelimünster → Walheim → Friesenrath
Aachen Region, North Rhine-Westphalia, Germany
=============================================================================
Author  : Joexy1286
Course  : Field Tunnel Mapping Training
Data    : GK50 (IS GK NRW), DGM1 (Geobasis NRW), QGIS EPSG:25832
Purpose : Feasibility-level geological-geotechnical assessment of a
          ~4.3 km tunnel alignment through Devonian-Carboniferous strata
=============================================================================
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch
from matplotlib.gridspec import GridSpec
from scipy.ndimage import uniform_filter1d

# ── Configuration ─────────────────────────────────────────────────────────
CSV_PATH       = "/mnt/user-data/uploads/profile_points_v2_lithology_v2.csv"
MIN_COVER      = 20.0    # m — minimum rock cover over tunnel invert
FAULT_CH       = 1800    # m — Breinigerberg Überschiebung (approx chainage)
FAULT_WIDTH    = 60      # m — damage zone half-width
TUNNEL_GRADE   = -0.003  # m/m — slight downgrade portal to portal

# ── Formation colour scheme (GK50 standard palette adapted) ──────────────
FORM_CONFIG = {
    "dfrsf+fafs": {
        "label": "Schmidthof-Fm. + Famenne Schiefer\n(Frasnium–Famennium)",
        "color": "#8B6914", "hatch": None,   "short": "dFrs+Fafs",
        "risk": "moderate"
    },
    "dfrsfkk": {
        "label": "Schmidthof-Fm., Frasnes-Knollenkalk\n(Frasnium)",
        "color": "#C8963E", "hatch": "///",  "short": "dFrsfkk",
        "risk": "high"    # carbonate — karst risk
    },
    "dvfrmk": {
        "label": "Friesenrath-Formation\n(Mitteldevon)",
        "color": "#6B8E6B", "hatch": None,   "short": "dvFrm",
        "risk": "low"
    },
    "dfaes-ev": {
        "label": "Esneux-Fm. bis Evieux-Fm.\n(Condroz-Sandstein, Famennium)",
        "color": "#B8860B", "hatch": "...",  "short": "dFaes-ev",
        "risk": "low"
    },
    "devfr": {
        "label": "Fleuth-Schichten\n(quadrigeminum-Schichten)",
        "color": "#556B5C", "hatch": None,   "short": "devfr",
        "risk": "low"
    },
    "ctmk": {
        "label": "Terwagne-Fm. + Neffe-Fm.\n(Oberer Kohlenkalk, Tournaisium)",
        "color": "#7EB3D8", "hatch": "xxx",  "short": "ctmk",
        "risk": "very high"  # limestone — major karst risk
    },
    "cvtene": {
        "label": "Hastière-Fm. / Pont d'Arcole-Fm.\n(Mittlerer Kohlenkalk, Viséum)",
        "color": "#4A86B8", "hatch": "xxx",  "short": "cvtene",
        "risk": "very high"
    },
    "dvflq": {
        "label": "Massenkalk (ungegliedert)\n(Givetium–Frasnium)",
        "color": "#A0C0D8", "hatch": "///",  "short": "dvflq",
        "risk": "high"
    },
}

BG    = "#0d1117"
PANEL = "#161b22"
WHITE = "#f0f6fc"
MUTED = "#8b949e"
RED   = "#f85149"
GOLD  = "#e3b341"
STEEL = "#58a6ff"

# ═══════════════════════════════════════════════════════════════════════════
# LOAD & PREPARE DATA
# ═══════════════════════════════════════════════════════════════════════════
df = pd.read_csv(CSV_PATH).sort_values("distance").reset_index(drop=True)

x        = df["distance"].values.astype(float)
surface  = uniform_filter1d(df["elev_1"].values.astype(float), size=5)
bedrock  = np.minimum(
    uniform_filter1d(df["quatbase_1"].values.astype(float), size=5),
    surface
)
overburden = surface - bedrock
anomaly  = df["overburden_m"].values < 0

# Tunnel invert — straight grade, min 20 m below bedrock top minimum
tunnel_start = bedrock.max() - MIN_COVER - 5
tunnel_end   = tunnel_start + TUNNEL_GRADE * (x[-1] - x[0])
tunnel_invert = np.interp(x, [x[0], x[-1]], [tunnel_start, tunnel_end])
tunnel_crown  = tunnel_invert + 8.5   # 8.5 m tunnel diameter

print(f"  Alignment: {x[0]:.0f} – {x[-1]:.0f} m  ({(x[-1]-x[0])/1000:.2f} km)")
print(f"  Surface:   {surface.min():.1f} – {surface.max():.1f} m asl")
print(f"  Bedrock:   {bedrock.min():.1f} – {bedrock.max():.1f} m asl")
print(f"  Overburden: {overburden.min():.1f} – {overburden.max():.1f} m")
print(f"  Tunnel invert: {tunnel_start:.1f} – {tunnel_end:.1f} m asl")
print(f"  Anomalies (TIN edge effects): {anomaly.sum()} points")
print(f"  Formations: {df['SYMBOL'].nunique()}")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — MAIN GEOLOGICAL-GEOTECHNICAL CROSS SECTION
# ═══════════════════════════════════════════════════════════════════════════
print("\n  Rendering Figure 1: Main cross section...")

fig = plt.figure(figsize=(22, 13), facecolor=BG)
fig.suptitle(
    "GEOLOGICAL-GEOTECHNICAL CROSS SECTION\n"
    "Tunnel Alignment: Kornelimünster → Walheim → Friesenrath  ·  "
    "Aachen Region, NRW, Germany  ·  GK50 / DGM1 (Geobasis NRW)",
    fontsize=10, color=WHITE, fontweight='bold', y=0.98
)

gs = GridSpec(3, 1, figure=fig, height_ratios=[6, 1.2, 0.8],
              hspace=0.08, left=0.06, right=0.97, top=0.92, bottom=0.06)

ax_sec  = fig.add_subplot(gs[0])   # main cross section
ax_cov  = fig.add_subplot(gs[1])   # overburden profile
ax_haz  = fig.add_subplot(gs[2])   # hazard zonation strip

for ax in [ax_sec, ax_cov, ax_haz]:
    ax.set_facecolor(PANEL)
    ax.set_xlim(x[0], x[-1])
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(MUTED)

# ── Main cross section ────────────────────────────────────────────────────

# Fill geological formations between surface and bedrock
symbols = df["SYMBOL"].values
unique_sym = df["SYMBOL"].unique()

for sym in unique_sym:
    mask = symbols == sym
    if mask.sum() < 2:
        continue
    cfg = FORM_CONFIG.get(sym, {"color": "#888", "hatch": None})
    xi  = x[mask]
    si  = surface[mask]
    bi  = bedrock[mask]
    ax_sec.fill_between(xi, bi, si,
                        color=cfg["color"], alpha=0.85,
                        hatch=cfg.get("hatch"),
                        linewidth=0.3, edgecolor="#00000033",
                        label=cfg.get("label", sym))

# Quaternary cover (surface to bedrock where overburden > 0)
ax_sec.fill_between(x, bedrock, surface,
                    where=overburden > 0.5,
                    color="#D4C4A0", alpha=0.5, linewidth=0,
                    label="Quaternary cover / Eluvium")

# Surface topography line
ax_sec.plot(x, surface, color=WHITE, lw=1.2, zorder=10)

# Bedrock top line
ax_sec.plot(x, bedrock, color="#FFD700", lw=1.0, ls='--',
            zorder=10, label="Bedrock surface (Präquartärer Untergrund)")

# Tunnel envelope
ax_sec.fill_between(x, tunnel_invert, tunnel_crown,
                    color="#1a1a2e", alpha=0.9, zorder=12,
                    label="Tunnel envelope (D=8.5 m)")
ax_sec.plot(x, tunnel_invert, color=STEEL, lw=1.5, zorder=13)
ax_sec.plot(x, tunnel_crown,  color=STEEL, lw=0.8, ls=':', zorder=13)

# Portal markers
for px, label in [(x[0], "Portal N\n(Kornelimünster)"),
                  (x[-1], "Portal S\n(Friesenrath)")]:
    ax_sec.axvline(px + (30 if px == x[0] else -30),
                   color=STEEL, lw=1.0, ls='--', alpha=0.6, zorder=11)
    ax_sec.text(px + (60 if px == x[0] else -60),
                tunnel_invert[0 if px == x[0] else -1] + 15,
                label, color=STEEL, fontsize=7, ha='left' if px == x[0] else 'right',
                fontweight='bold')

# Fault zone — Breinigerberg Überschiebung
ax_sec.axvspan(FAULT_CH - FAULT_WIDTH, FAULT_CH + FAULT_WIDTH,
               color=RED, alpha=0.15, zorder=9)
ax_sec.axvline(FAULT_CH, color=RED, lw=1.5, ls='-', zorder=11)
ax_sec.text(FAULT_CH + 5, surface.max() - 5,
            "Breinigerberg\nÜberschiebung\n(~38 m offset)",
            color=RED, fontsize=7, fontweight='bold', va='top')

# Minimum cover reference line
ax_sec.axhline(tunnel_start + MIN_COVER, color=GOLD, lw=0.8,
               ls=':', alpha=0.7, zorder=8)
ax_sec.text(x[-1] - 50, tunnel_start + MIN_COVER + 1,
            f"Min. cover {MIN_COVER:.0f} m", color=GOLD, fontsize=7, ha='right')

# Anomaly flags
anom_x = x[anomaly]
if len(anom_x) > 0:
    anom_y = surface[anomaly]
    ax_sec.scatter(anom_x, anom_y, marker='v', color=GOLD,
                   s=25, zorder=14, label=f"TIN edge anomalies (n={anomaly.sum()})")

# Chainage ticks
for ch in range(0, int(x[-1]) + 1, 500):
    ax_sec.axvline(ch, color=MUTED, lw=0.3, alpha=0.4, zorder=1)
    ax_sec.text(ch, surface.min() - 3, f"Ch.{ch}", color=MUTED,
                fontsize=6, ha='center', va='top')

ax_sec.set_ylabel("Elevation (m asl)", color=WHITE, fontsize=9)
ax_sec.set_ylim(tunnel_invert.min() - 20, surface.max() + 12)
ax_sec.set_xticks([])
ax_sec.grid(True, axis='y', color='#21262d', lw=0.4)

# Legend — two columns
handles, labels = ax_sec.get_legend_handles_labels()
ax_sec.legend(handles, labels, loc='upper right', fontsize=6,
              facecolor=PANEL, edgecolor=MUTED, ncol=2,
              framealpha=0.9, markerscale=1.2)

# Scale bar
ax_sec.annotate('', xy=(500, surface.min() - 8), xytext=(0, surface.min() - 8),
                arrowprops=dict(arrowstyle='<->', color=WHITE, lw=1.2))
ax_sec.text(250, surface.min() - 6, "500 m", color=WHITE,
            fontsize=7, ha='center', fontweight='bold')

# ── Overburden profile ────────────────────────────────────────────────────
ax_cov.fill_between(x, 0, overburden, where=overburden >= 0,
                    color=STEEL, alpha=0.6)
ax_cov.fill_between(x, 0, overburden, where=overburden < 0,
                    color=RED, alpha=0.8)
ax_cov.axhline(MIN_COVER, color=GOLD, lw=1.0, ls='--',
               label=f"Min. cover ({MIN_COVER:.0f} m)")
ax_cov.axhline(0, color=WHITE, lw=0.5)
ax_cov.axvline(FAULT_CH, color=RED, lw=1.0, ls='-', alpha=0.6)
ax_cov.set_ylabel("Rock cover\n(m)", color=WHITE, fontsize=8)
ax_cov.set_ylim(-20, overburden.max() + 5)
ax_cov.set_xticks([])
ax_cov.legend(fontsize=7, facecolor=PANEL, edgecolor=MUTED, loc='upper right')
ax_cov.grid(True, axis='y', color='#21262d', lw=0.4)
ax_cov.text(x[-1] - 50, -15,
            f"{(overburden < MIN_COVER).sum()} pts < {MIN_COVER:.0f} m cover",
            color=GOLD, fontsize=7, ha='right')

# ── Hazard zonation strip ─────────────────────────────────────────────────
HAZARD_MAP = {
    "ctmk":     3,  # very high
    "cvtene":   3,
    "dfrsfkk":  2,  # high
    "dvflq":    2,
    "dfrsf+fafs": 1,  # moderate
    "dvfrmk":   0,
    "dfaes-ev": 0,
    "devfr":    0,
}
HAZARD_COLORS = {0: "#2ea043", 1: "#e3b341", 2: "#f85149", 3: "#8B0000"}
HAZARD_LABELS = {0: "Low", 1: "Moderate", 2: "High", 3: "Very High"}

hazard = np.array([HAZARD_MAP.get(s, 1) for s in symbols])
for i in range(len(x) - 1):
    ax_haz.fill_between(
        [x[i], x[i+1]], [0, 0], [1, 1],
        color=HAZARD_COLORS[hazard[i]], alpha=0.85, linewidth=0
    )
ax_haz.axvline(FAULT_CH, color=RED, lw=1.5, alpha=0.9)
ax_haz.set_xlim(x[0], x[-1])
ax_haz.set_ylim(0, 1)
ax_haz.set_yticks([])
ax_haz.set_xlabel("Chainage (m)", color=WHITE, fontsize=9)
ax_haz.set_ylabel("Hazard\nZone", color=WHITE, fontsize=7, rotation=0,
                  ha='right', va='center', labelpad=40)

# Hazard legend
legend_patches = [mpatches.Rectangle((0,0), 1, 1, color=HAZARD_COLORS[lvl],
                  alpha=0.85, label=HAZARD_LABELS[lvl]) for lvl in range(4)]
ax_haz.legend(handles=legend_patches, loc='lower right', fontsize=7, facecolor=PANEL,
              edgecolor=MUTED, ncol=4, framealpha=0.9)

# Chainage labels on bottom axis
ax_haz.set_xticks(range(0, int(x[-1]) + 1, 500))
ax_haz.tick_params(axis='x', colors=MUTED, labelsize=8)

plt.savefig("/home/claude/tunnel-portfolio/figures/01_geological_cross_section.png",
            dpi=200, bbox_inches='tight', facecolor=BG)
plt.close()
print("  ✓ Figure 1 saved")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2 — FORMATION STATISTICS & GEOTECHNICAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print("  Rendering Figure 2: Formation statistics...")

fig, axes = plt.subplots(1, 3, figsize=(18, 7), facecolor=BG)
fig.suptitle(
    "FORMATION STATISTICS & GEOTECHNICAL SUMMARY  ·  "
    "Kornelimünster–Friesenrath Tunnel Alignment",
    fontsize=10, color=WHITE, fontweight='bold', y=0.98
)

# Formation distribution along alignment
form_lengths = {}
for sym in unique_sym:
    mask = symbols == sym
    xi = x[mask]
    if len(xi) > 1:
        form_lengths[sym] = xi[-1] - xi[0]
    else:
        form_lengths[sym] = 10

sorted_forms = sorted(form_lengths.items(), key=lambda v: v[1], reverse=True)
labels_bar = [FORM_CONFIG.get(s[0], {}).get("short", s[0]) for s in sorted_forms]
values_bar = [s[1] for s in sorted_forms]
colors_bar = [FORM_CONFIG.get(s[0], {}).get("color", "#888") for s in sorted_forms]

axes[0].barh(labels_bar, values_bar, color=colors_bar, alpha=0.85, edgecolor=BG)
axes[0].set_xlabel("Approximate extent along alignment (m)", color=WHITE, fontsize=8)
axes[0].set_title("Formation Distribution", color=WHITE, fontsize=9, fontweight='bold')
axes[0].set_facecolor(PANEL)
axes[0].tick_params(colors=MUTED, labelsize=8)
axes[0].axvline(500, color=MUTED, lw=0.5, ls='--', alpha=0.5)
axes[0].axvline(1000, color=MUTED, lw=0.5, ls='--', alpha=0.5)

# Overburden histogram
axes[1].hist(overburden[overburden >= 0], bins=30,
             color=STEEL, alpha=0.8, edgecolor=BG)
axes[1].axvline(MIN_COVER, color=GOLD, lw=1.5, ls='--',
                label=f"Min. cover ({MIN_COVER:.0f} m)")
axes[1].axvline(overburden[overburden >= 0].mean(), color=WHITE, lw=1.2, ls='-',
                label=f"Mean = {overburden[overburden>=0].mean():.1f} m")
axes[1].set_xlabel("Rock cover above tunnel (m)", color=WHITE, fontsize=8)
axes[1].set_ylabel("Count (10 m intervals)", color=WHITE, fontsize=8)
axes[1].set_title("Overburden Distribution", color=WHITE, fontsize=9, fontweight='bold')
axes[1].set_facecolor(PANEL)
axes[1].tick_params(colors=MUTED, labelsize=8)
axes[1].legend(fontsize=7, facecolor=PANEL, edgecolor=MUTED)

# Hazard pie chart
hazard_counts = {HAZARD_LABELS[k]: np.sum(hazard == k) for k in range(4)}
haz_colors = [HAZARD_COLORS[k] for k in range(4)]
wedges, texts, autotexts = axes[2].pie(
    hazard_counts.values(),
    labels=hazard_counts.keys(),
    colors=haz_colors,
    autopct='%1.1f%%',
    startangle=90,
    textprops={'color': WHITE, 'fontsize': 8},
    wedgeprops={'edgecolor': BG, 'linewidth': 1.5}
)
for at in autotexts:
    at.set_color(WHITE)
    at.set_fontsize(8)
axes[2].set_title("Geotechnical Hazard Zonation\n(% of alignment length)",
                  color=WHITE, fontsize=9, fontweight='bold')
axes[2].set_facecolor(PANEL)

for ax in axes:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(MUTED)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("/home/claude/tunnel-portfolio/figures/02_formation_statistics.png",
            dpi=200, bbox_inches='tight', facecolor=BG)
plt.close()
print("  ✓ Figure 2 saved")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3 — SITE INVESTIGATION PROGRAMME
# ═══════════════════════════════════════════════════════════════════════════
print("  Rendering Figure 3: Site investigation programme...")

fig, ax = plt.subplots(figsize=(20, 6), facecolor=BG)
ax.set_facecolor(PANEL)
ax.set_xlim(x[0], x[-1])
ax.set_ylim(0, 6)
ax.set_yticks([])
ax.set_xlabel("Chainage (m)", color=WHITE, fontsize=9)
ax.set_title(
    "SITE INVESTIGATION PROGRAMME  ·  Geophysics-first strategy with targeted boreholes\n"
    "Kornelimünster–Friesenrath Tunnel Alignment",
    color=WHITE, fontsize=10, fontweight='bold'
)
ax.set_facecolor(PANEL)
ax.tick_params(colors=MUTED, labelsize=8)

# Background hazard strip
for i in range(len(x) - 1):
    ax.fill_between([x[i], x[i+1]], [0, 0], [1, 1],
                    color=HAZARD_COLORS[hazard[i]], alpha=0.3, linewidth=0)

# Geophysical survey lines
ax.annotate('', xy=(x[-1]-50, 1.5), xytext=(x[0]+50, 1.5),
            arrowprops=dict(arrowstyle='->', color=STEEL, lw=2.0))
ax.text(x[-1]/2, 1.7, "2D ERT + Seismic Refraction Profile (full alignment)",
        color=STEEL, fontsize=8, ha='center', fontweight='bold')

# Targeted boreholes at high-risk zones
borehole_clusters = [
    (300,  "BH-1\n(Portal N\nstability)", "#2ea043"),
    (800,  "BH-2\n(Karst\nscreening)", RED),
    (1750, "BH-3\n(Fault zone\nappraisal)", RED),
    (1850, "BH-4\n(Fault zone\nappraisal)", RED),
    (2400, "BH-5\n(Cover\n<20m zone)", GOLD),
    (3200, "BH-6\n(Limestone\nkarst)", "#8B0000"),
    (3900, "BH-7\n(Portal S\nstability)", "#2ea043"),
]

for ch, label, col in borehole_clusters:
    ax.annotate('', xy=(ch, 1.1), xytext=(ch, 2.8),
                arrowprops=dict(arrowstyle='->', color=col, lw=1.8))
    ax.scatter([ch], [2.9], marker='o', s=80, color=col,
               edgecolors=WHITE, linewidth=1.0, zorder=10)
    ax.text(ch, 3.2, label, color=col, fontsize=6.5,
            ha='center', va='bottom', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=PANEL,
                      edgecolor=col, alpha=0.8))

# Water level monitoring note
ax.text(x[-1]/2, 4.8,
        "Groundwater monitoring: standpipe piezometers in BH-2, BH-3, BH-6 "
        "— minimum 6-month baseline prior to construction",
        color=MUTED, fontsize=7.5, ha='center', style='italic')

# Chainage markers
for ch in range(0, int(x[-1]) + 1, 500):
    ax.axvline(ch, color=MUTED, lw=0.4, alpha=0.4)
    ax.text(ch, 0.1, f"Ch.{ch}", color=MUTED, fontsize=6.5, ha='center')

ax.axvline(FAULT_CH, color=RED, lw=1.5, ls='--', alpha=0.8, zorder=8)
ax.text(FAULT_CH + 10, 0.5, "Fault", color=RED, fontsize=7, rotation=90)

ax.set_xticks(range(0, int(x[-1])+1, 500))

plt.tight_layout()
plt.savefig("/home/claude/tunnel-portfolio/figures/03_site_investigation.png",
            dpi=200, bbox_inches='tight', facecolor=BG)
plt.close()
print("  ✓ Figure 3 saved")

# ═══════════════════════════════════════════════════════════════════════════
# PRINT SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════
print("\n  FORMATION SUMMARY TABLE")
print("  " + "─"*80)
summary_data = []
for sym in df['SYMBOL'].unique():
    sub = df[df['SYMBOL'] == sym]
    cfg = FORM_CONFIG.get(sym, {})
    summary_data.append({
        "Symbol": sym,
        "Formation": cfg.get("short", sym),
        "Points": len(sub),
        "Distance_m": f"{sub['distance'].min():.0f}–{sub['distance'].max():.0f}",
        "Mean_Cover_m": f"{(sub['elev_1'] - sub['quatbase_1']).mean():.1f}",
        "Hazard": cfg.get("risk", "–"),
    })
summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))
print("\n  ✓ All figures complete")
