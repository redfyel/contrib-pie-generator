import subprocess
import matplotlib.pyplot as plt
import sys
from collections import defaultdict
import re
import numpy as np
from matplotlib import colors as mcolors

# === INPUTS ===
chart_size = sys.argv[1] if len(sys.argv) > 1 else '6,6'
width, height = map(int, chart_size.split(','))
palette = [c.strip() for c in sys.argv[2].split(',')] if len(sys.argv) > 2 else None

# === GATHER GIT LOG DATA ===
log_output = subprocess.check_output(["git", "log", "--pretty=format:%an||%ae"]).decode("utf-8")
lines = log_output.strip().split("\n")

# === MERGE CONTRIBUTORS ===
contributor_commits = defaultdict(int)
id_to_display = {}
bot_count = 0

for line in lines:
    try:
        name, email = line.split("||")
    except ValueError:
        continue

    name = name.strip()
    email = email.strip()

    if "github-actions[bot]" in name:
        bot_count += 1
        continue

    match = re.match(r"(.*)@users\.noreply\.github\.com", email)
    if match:
        username = match.group(1).lower()
        display = f"{username} ({name})" if username != name.lower() else username
        contributor_id = username
    else:
        contributor_id = email.lower()
        display = contributor_id

    if contributor_id not in id_to_display:
        id_to_display[contributor_id] = display

    contributor_commits[contributor_id] += 1

# === APPEND BOT ===
if bot_count > 0:
    contributor_commits["bot"] = bot_count
    id_to_display["bot"] = "github-actions[bot]"

# === PREPARE FINAL DATA ===
ordered_ids = list(contributor_commits.keys())
labels = [id_to_display[cid] for cid in ordered_ids]
sizes = [contributor_commits[cid] for cid in ordered_ids]

# === SHADE SMARTNESS ===
def is_dark(color_rgb):
    r, g, b = color_rgb
    luminance = 0.299*r + 0.587*g + 0.114*b
    return luminance < 0.5

def generate_balanced_shades(base_colors, total_needed):
    base_rgb = [np.array(mcolors.to_rgb(c)) for c in base_colors]
    output = []
    shade_steps = (total_needed // len(base_rgb)) + 1

    for base in base_rgb:
        dark = is_dark(base)
        for i in range(shade_steps):
            factor = 1 + (i * 0.1) if not dark else 1 - (i * 0.15)
            shaded = np.clip(base * factor, 0, 1)
            output.append(tuple(shaded))
            if len(output) == total_needed:
                return output
    return output[:total_needed]

if palette:
    pie_colors = generate_balanced_shades(palette, len(labels))
else:
    pie_colors = plt.get_cmap("tab20c").colors[:len(labels)]

# === PLOT PIE CHART ===
plt.figure(figsize=(width, height))
wedges, texts, autotexts = plt.pie(
    sizes,
    labels=None,
    colors=pie_colors,
    autopct="%1.1f%%",
    startangle=140,
    textprops={'color': 'white', 'fontsize': 12},
    wedgeprops={'edgecolor': 'black', 'linewidth': 1}
)

# === LEGEND: Contributors on side, bot at bottom ===
sorted_legend = [(w, l) for w, l in zip(wedges, labels) if "bot" not in l.lower()]
bot_legend = [(w, l) for w, l in zip(wedges, labels) if "bot" in l.lower()]
final_legend = sorted_legend + bot_legend

wedges_for_legend, labels_for_legend = zip(*final_legend)
plt.legend(wedges_for_legend, labels_for_legend, title="Contributors", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)

plt.axis("equal")
plt.title("Contributions by Commits", fontsize=16, fontweight='bold')
plt.savefig("contributor-pie.png", bbox_inches="tight")
plt.show()
