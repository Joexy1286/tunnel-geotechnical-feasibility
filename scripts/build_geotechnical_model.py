import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
from matplotlib.path import Path
from pyproj import Geod

# ==================================================================
# CONFIG (same base geology/dip data as the earlier cross section)
# ==================================================================
PROFILE_CSV = "/mnt/user-data/uploads/profile_points_v2_lithology_v2.csv"
OUTPUT_PATH = "/mnt/user-data/outputs/three_panel_model.png"
MIN_ROCK_COVER = 20
PORTAL_EXCAVATION = 5
FAULT_CHAINAGE_RANGE = (1200, 1600)
PORTAL_N = (50.732141, 6.176468)
PORTAL_S = (50.693782, 6.179473)
KARST_KEYWORDS = ["Kalkstein", "Dolomitstein", "Massenkalk"]
CONTROL = [(0, 35.25, 310.27), (1210, 37.0, 327.3), (2750, 36.7, 338.0),
           (2850, 32.8, 336.2), (3600, 55.0, 340.3)]

# ==================================================================
# LOAD + GEOLOGICAL MODEL (same logic as cross_section_v3)
# ==================================================================
df = pd.read_csv(PROFILE_CSV).sort_values("distance").reset_index(drop=True)
df["anomaly"] = df["overburden_m"] < 0
df["bedrock_top"] = np.minimum(df["quatbase_1"], df["elev_1"])
x = df["distance"].values
surface = df["elev_1"].values
bedrock_top = df["bedrock_top"].values

geod = Geod(ellps="WGS84")
fwd_az, _, _ = geod.inv(PORTAL_N[1], PORTAL_N[0], PORTAL_S[1], PORTAL_S[0])
tunnel_bearing = fwd_az % 360

def angdiff(a, b):
    return abs((a - b + 180) % 360 - 180)

ctrl_x = np.array([c[0] for c in CONTROL])
ctrl_dip = np.array([c[1] for c in CONTROL])
ctrl_dir_sin = np.sin(np.radians([c[2] for c in CONTROL]))
ctrl_dir_cos = np.cos(np.radians([c[2] for c in CONTROL]))
xr = np.linspace(x.min(), x.max(), 800)
local_dip = np.interp(xr, ctrl_x, ctrl_dip, left=ctrl_dip[0], right=ctrl_dip[-1])
local_dir_sin = np.interp(xr, ctrl_x, ctrl_dir_sin, left=ctrl_dir_sin[0], right=ctrl_dir_sin[-1])
local_dir_cos = np.interp(xr, ctrl_x, ctrl_dir_cos, left=ctrl_dir_cos[0], right=ctrl_dir_cos[-1])
local_dipdir = np.degrees(np.arctan2(local_dir_sin, local_dir_cos)) % 360
beta_arr = np.array([min(angdiff(d, tunnel_bearing), angdiff(d, (tunnel_bearing + 180) % 360)) for d in local_dipdir])
apparent_dip_arr = np.degrees(np.arctan(np.tan(np.radians(local_dip)) * np.cos(np.radians(beta_arr))))
updip_az_arr = (local_dipdir + 180) % 360
shallow_arr = np.array([angdiff(u, tunnel_bearing) < angdiff(d, tunnel_bearing) for u, d in zip(updip_az_arr, local_dipdir)])
slope_arr = np.where(shallow_arr, 1.0, -1.0) * np.tan(np.radians(apparent_dip_arr))

def integrate_trace(chainage_ref, elev_ref):
    trace = np.zeros_like(xr)
    idx_ref = min(max(np.searchsorted(xr, chainage_ref), 0), len(xr) - 1)
    trace[idx_ref] = elev_ref
    for i in range(idx_ref + 1, len(xr)):
        trace[i] = trace[i - 1] + slope_arr[i - 1] * (xr[i] - xr[i - 1])
    for i in range(idx_ref - 1, -1, -1):
        trace[i] = trace[i + 1] - slope_arr[i] * (xr[i + 1] - xr[i])
    return trace

changes = df["EINHEIT"] != df["EINHEIT"].shift(1)
contact_rows = df.index[changes][1:]
contacts = []
for i in contact_rows:
    prev, curr = df.loc[i - 1], df.loc[i]
    contacts.append({"chainage": (prev["distance"] + curr["distance"]) / 2,
                      "elevation": (prev["elev_1"] + curr["elev_1"]) / 2})
bounds = [x.min()] + [c["chainage"] for c in contacts] + [x.max()]
zone_units = []
for i in range(len(bounds) - 1):
    mid = (bounds[i] + bounds[i + 1]) / 2
    row = df.iloc[(df["distance"] - mid).abs().argsort()[:1]]
    zone_units.append(row["EINHEIT"].values[0])

def short_name(s):
    return s.split(" und ")[0].split(",")[0][:32]

zone_short = [short_name(u) for u in zone_units]
zone_karst = [any(k in (df.loc[df["EINHEIT"] == u, "LITHOLOGIE"].iloc[0] if (df["EINHEIT"] == u).any() else "") for k in KARST_KEYWORDS) for u in zone_units]

bedrock_top_interp = np.interp(xr, x, bedrock_top)
plot_floor = surface.min() - 60
boundary_lines = [bedrock_top_interp] + [integrate_trace(c["chainage"], c["elevation"]) for c in contacts] + [np.full_like(xr, plot_floor)]
boundary_stack = np.vstack(boundary_lines)
for i in range(1, boundary_stack.shape[0]):
    boundary_stack[i] = np.minimum(boundary_stack[i], boundary_stack[i - 1])

invert_n = surface[0] - PORTAL_EXCAVATION
invert_s = surface[-1] - PORTAL_EXCAVATION
grade_slope = (invert_s - invert_n) / (x[-1] - x[0])
tunnel_invert = invert_n + grade_slope * (x - x[0])
tunnel_invert_r = invert_n + grade_slope * (xr - x[0])

# ==================================================================
# ROCK MASS TABLE -- updated with confirmed per-outcrop Schmidt hammer
# data (Outcrops 1,2 -> Terwagne; 6,10 -> Schmidthof Schiefer;
# 4+5 -> Schmidthof Knollenkalk). Zones with NO outcrop-level
# measurement are marked explicitly as unconfirmed estimates -- the
# earlier "southern/northern" summary did not reliably attribute to
# named outcrops and is NOT carried over here.
# ==================================================================
rock_mass = [
    dict(grade="R5-R6", ucs="159 MPa mean (41-80, n=12)", gsi="~55-65 (est.)", quality="Good"),          # Terwagne
    dict(grade="n/a", ucs="No data", gsi="~45-55 (est.)", quality="Moderate (no data)"),                   # Hastiere
    dict(grade="n/a", ucs="No data", gsi="~50-60 (est.)", quality="Moderate (no data)"),                   # Esneux/Evieux
    dict(grade="R1-R2 / R4-R5", ucs="Intact 145 MPa / jointed 20-31 MPa (+3rd R=0 confirm)", gsi="~20-35 (est.)",
         quality="Poor (variable)"),                                                                        # Schmidthof Schiefer
    dict(grade="R5", ucs="179 MPa mean (50-57, n=3)", gsi="~55-65 (est.)", quality="Good"),                # Schmidthof Knollenkalk
    dict(grade="R4-R5 / R2-R3", ucs="Intact ~255 MPa / jointed ~52 MPa (southern traverse, unconfirmed exact station)",
         gsi="~40-55 (est.)", quality="Good-Moderate (variable)"),                                          # Massenkalk
    dict(grade="R4-R5 / R2-R3", ucs="Intact ~255 MPa / jointed ~52 MPa (southern traverse, unconfirmed exact station)",
         gsi="~40-55 (est.)", quality="Good-Moderate (variable)"),                                          # Fleuth-Schichten
    dict(grade="R4-R5 / R2-R3", ucs="Intact ~255 MPa / jointed ~52 MPa (southern traverse, unconfirmed exact station)",
         gsi="~40-55 (est.)", quality="Good-Moderate (variable)"),                                          # Friesenrath
]
quality_color = {"Poor (variable)": "#c0392b", "Moderate (no data)": "#e0a030", "Good": "#5a9e5a",
                  "Good-Moderate (variable)": "#7fae4a", "Good-V.good": "#2e7d4f", "Very poor": "#c0392b"}
# Massenkalk / Fleuth-Schichten / Friesenrath share one uncertain data point (southern
# traverse) but remain three distinct formations -- give each its own shade so they
# don't visually merge into a single block, per formation identity in Panel 1
zone_override_color = {5: "#6f9e3f", 6: "#8fbf5a", 7: "#4f8a35"}

# behavior: Massenkalk/Fleuth/Friesenrath upgraded to Ravelling given confirmed jointed-zone
# weakness (R2-R3, ~52 MPa) even though intact rock is strong
behavior_base = ["Stable", "Stable", "Stable", "Squeezing", "Stable", "Ravelling (karst)", "Ravelling", "Ravelling"]
support_class = {"Stable": "Class I - spot bolting", "Ravelling": "Class II - systematic bolts + mesh/shotcrete",
                  "Ravelling (karst)": "Class II - bolts/shotcrete + water control", "Squeezing": "Class III - steel sets + shotcrete"}
behavior_color = {"Stable": "#5a9e5a", "Ravelling": "#e0a030", "Ravelling (karst)": "#4aa0c9", "Squeezing": "#c0392b"}

# ==================================================================
# PLOT -- 3 stacked panels
# ==================================================================
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(19, 18.5), sharex=True,
                                          gridspec_kw={'height_ratios': [1.1, 1.1, 1.0, 0.6]})
palette = plt.cm.Set2(np.linspace(0, 1, max(len(zone_short), 2)))
ylim = (tunnel_invert.min() - 15, surface.max() + 20)
# All three panels share ONE offset so a given absolute elevation always displays
# the same relative number everywhere. Chosen so the lowest point on the section
# (ylim[0], the deepest tunnel invert) reads as 20m -- not absolute NHN, which
# looks like an implausible drilling depth for what is actually a shallow tunnel.
REL_OFFSET = ylim[0] - 20
rel_fmt = FuncFormatter(lambda val, pos: f"{val - REL_OFFSET:.0f}")

# ---------- PANEL 1: Geological Model ----------
for i in range(len(zone_short)):
    ax1.fill_between(xr, boundary_stack[i + 1], boundary_stack[i], color=palette[i], zorder=1, linewidth=0)
    if zone_karst[i]:
        ax1.fill_between(xr, boundary_stack[i + 1], boundary_stack[i], facecolor="none", edgecolor="black",
                          hatch="///", alpha=0.35, linewidth=0, zorder=2)
for i in range(1, boundary_stack.shape[0] - 1):
    ax1.plot(xr, boundary_stack[i], color="#4a3b28", linewidth=0.7, alpha=0.6, zorder=3)
ax1.fill_between(x, bedrock_top, surface, color="#d9c9a3", zorder=4)
ax1.plot(x, surface, color="#4a3b28", linewidth=1.6, zorder=6)
ax1.plot(x, bedrock_top, color="#6b5842", linewidth=1, linestyle="--", zorder=5)
ax1.axvspan(*FAULT_CHAINAGE_RANGE, color="#8e44ad", alpha=0.18, zorder=8)
ax1.text(np.mean(FAULT_CHAINAGE_RANGE), surface.max() + 8, "Fault zone", ha="center", fontsize=8, color="#6b3fa0")
for name, c in zip(zone_short, palette):
    ax1.fill_between([], [], color=c, label=name)
ax1.legend(loc="lower left", fontsize=6.5, framealpha=0.92, ncol=1)
ax1.set_ylim(*ylim)
ax1.yaxis.set_major_formatter(rel_fmt)
ax1.set_ylabel("Elevation (m, relative)", fontsize=10)
ax1.set_title("1. Geological Model", fontsize=12, fontweight="bold", loc="left")

# ---------- PANEL 2: Rock Mass Model ----------
for i in range(len(zone_short)):
    q = rock_mass[i]["quality"]
    fill_color = zone_override_color.get(i, quality_color.get(q, "#999"))
    ax2.fill_between(xr, boundary_stack[i + 1], boundary_stack[i], color=fill_color,
                      alpha=0.8, zorder=1, linewidth=0)
for i in range(1, boundary_stack.shape[0] - 1):
    ax2.plot(xr, boundary_stack[i], color="#333", linewidth=0.6, alpha=0.5, zorder=3)
ax2.plot(x, surface, color="#4a3b28", linewidth=1.3, zorder=6)
ax2.axvspan(*FAULT_CHAINAGE_RANGE, color="#8e44ad", alpha=0.15, zorder=8)
for i in range(len(zone_short)):
    if i in (5, 6, 7):
        continue  # handled as one combined annotation below
    mid = (bounds[i] + bounds[i + 1]) / 2
    top_y = np.interp(mid, x, surface)
    rm = rock_mass[i]
    label = f"{rm['gsi']}\n{rm['ucs']}\nGrade {rm['grade']}\n{rm['quality']}"
    ax2.annotate(label, (mid, top_y + 10), fontsize=6, ha="center", va="bottom",
                 bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#888", alpha=0.9), zorder=10)

# combined annotation for Massenkalk/Fleuth/Friesenrath (identical southern-traverse data)
south_mid = (bounds[5] + bounds[8]) / 2
south_top = np.interp(south_mid, x, surface) + 10
rm = rock_mass[5]
label = (f"Massenkalk / Fleuth-Schichten / Friesenrath (combined)\n{rm['gsi']}\n{rm['ucs']}\n"
         f"Grade {rm['grade']}\n{rm['quality']}")
ax2.annotate(label, (south_mid, south_top + 10), fontsize=6, ha="center", va="bottom",
             bbox=dict(boxstyle="round,pad=0.3", fc="#fff8e8", ec="#888", alpha=0.95), zorder=10)

# real Schmidt hammer sample locations (confirmed outcrops only) -- placed low,
# in open space, to avoid colliding with the zone annotation boxes above.
# Outcrops 6 & 10 sit only 20 m apart, so their labels are staggered vertically.
marker_y = ylim[0] + 16
schmidt_outcrops = [(0, "Outcrops\n1+2, n=12", 0), (3080, "Outcrop 6\nn=12", 0),
                     (3240, "Outcrop 10\nn=2", 0), (3600, "Outcrops\n4+5, n=3", 0)]
for cx, lbl, yoff in schmidt_outcrops:
    ax2.scatter([cx], [marker_y], marker="v", color="black", s=45, zorder=11)
    ax2.annotate(lbl, (cx, marker_y - 3 + yoff), fontsize=5.5, ha="center", va="top", color="#333", zorder=11)
for q, c in quality_color.items():
    if q == "Good-Moderate (variable)":
        continue  # replaced below with per-formation entries
    ax2.fill_between([], [], color=c, alpha=0.8, label=q)
zone_labels_override = {5: "Massenkalk (variable)", 6: "Fleuth-Schichten (variable)", 7: "Friesenrath (variable)"}
for i, c in zone_override_color.items():
    ax2.fill_between([], [], color=c, alpha=0.8, label=zone_labels_override[i])
handles, labels = ax2.get_legend_handles_labels()
uniq = dict(zip(labels, handles))
ax2.legend(uniq.values(), uniq.keys(), loc="lower right", fontsize=7, framealpha=0.92)
ax2.set_ylim(ylim[0], ylim[1] + 15)
ax2.yaxis.set_major_formatter(rel_fmt)
ax2.set_ylabel("Elevation (m, relative)", fontsize=10)
ax2.set_title("2. Rock Mass - Predictive Description", fontsize=12, fontweight="bold", loc="left")

# ---------- PANEL 3: Rock Behavior Model ----------
# split zone 2 (Esneux/Evieux) at the fault so the fault stretch gets its own behavior
zone_bounds3 = list(bounds)
zone_behavior3 = list(behavior_base)
# find index of Esneux/Evieux zone (index 2) and splice fault sub-zone
esn_i = 2
fb_lo, fb_hi = FAULT_CHAINAGE_RANGE
insert_bounds = [zone_bounds3[esn_i], fb_lo, fb_hi, zone_bounds3[esn_i + 1]]
insert_behavior = ["Stable", "Squeezing", "Stable"]
zone_bounds3 = zone_bounds3[:esn_i] + insert_bounds + zone_bounds3[esn_i + 2:]
zone_behavior3 = zone_behavior3[:esn_i] + insert_behavior + zone_behavior3[esn_i + 1:]

for i in range(len(zone_behavior3)):
    b0, b1 = zone_bounds3[i], zone_bounds3[i + 1]
    beh = zone_behavior3[i]
    seg = xr[(xr >= b0) & (xr <= b1)]
    if len(seg) < 2:
        seg = np.array([b0, b1])
    surf_seg = np.interp(seg, x, surface)
    inv_seg = np.interp(seg, xr, tunnel_invert_r)
    ax3.fill_between(seg, inv_seg - 12, surf_seg, color=behavior_color[beh], alpha=0.55, zorder=1, linewidth=0)
ax3.plot(x, surface, color="#4a3b28", linewidth=1.3, zorder=6)
ax3.plot(x, tunnel_invert, color="black", linewidth=2, zorder=7)
# simple tunnel bore glyphs at a few stations
for cx in [400, 1600, 2100, 2950, 3450, 3700, 4000]:
    cy = np.interp(cx, x, tunnel_invert) + 4.5
    ax3.add_patch(mpatches.Ellipse((cx, cy), width=90, height=9, facecolor="white",
                                    edgecolor="black", linewidth=1, zorder=9))
ax3.axvspan(*FAULT_CHAINAGE_RANGE, color="none", edgecolor="#6b3fa0", linewidth=1.2, zorder=8)
for beh, c in behavior_color.items():
    ax3.fill_between([], [], color=c, alpha=0.55, label=f"{beh} ({support_class[beh]})")
ax3.legend(loc="lower left", fontsize=6.5, framealpha=0.92)
ax3.set_ylim(tunnel_invert.min() - 20, surface.max() + 15)
ax3.yaxis.set_major_formatter(rel_fmt)
ax3.set_ylabel("Elevation (m, relative)", fontsize=10)
ax3.set_title("3. Rock Behavior Model - predicted ground behavior & indicative support class",
              fontsize=12, fontweight="bold", loc="left")
ax3.text(0.995, 0.02, "Behavior classes are a first-pass estimate from GSI + structure/water context. "
                       "Not to true scale, vertical exaggerated. "
                       "Elevation shown relative to an arbitrary shallow datum, not absolute sea level.",
         transform=ax3.transAxes, fontsize=7.5, ha="right", color="gray", style="italic")

fig.suptitle("Geological-Geotechnical Longitudinal Section - Tunnel Alignment Kornelim\u00fcnster-Friesenrath - Group 4",
             fontsize=14, fontweight="bold", y=0.995)
# ---------- PANEL 4: Depth below ground surface (unambiguous small numbers) ----------
depth_below_surface = surface - tunnel_invert
ax4.fill_between(x, 0, depth_below_surface, color="#c0392b", alpha=0.25)
ax4.plot(x, depth_below_surface, color="#c0392b", linewidth=1.8)
ax4.axhline(MIN_ROCK_COVER, color="gray", linewidth=0.8, linestyle=":")
ax4.text(x.max(), MIN_ROCK_COVER, f" target cover {MIN_ROCK_COVER} m", fontsize=7, va="center", color="gray")
ax4.invert_yaxis()
ax4.set_ylabel("Depth below\nground surface (m)", fontsize=9)
ax4.set_xlabel("Chainage (m)", fontsize=11)
ax4.set_title("4. Depth Below Ground Surface (unambiguous check \u2014 not absolute elevation)",
              fontsize=12, fontweight="bold", loc="left")
ax4.grid(True, alpha=0.3, linewidth=0.5)
ax4.set_xlim(x.min(), x.max())

plt.tight_layout(rect=[0, 0, 1, 0.98])
plt.savefig(OUTPUT_PATH, dpi=180)
print("Saved:", OUTPUT_PATH)
