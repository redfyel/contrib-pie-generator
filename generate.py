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

    if "github-actions[bot]" in name:
        bot_count += 1
        continue

    # Extract GitHub username if possible
    match = re.match(r"(.*)@users\.noreply\.github\.com", email)
    if match:
        username = match.group(1).lower()
        display = username if name.lower() == username else f"{username} ({name})"
        user_id = username
    else:
        # Fallback to email username
        username = email.split("@")[0].lower()
        display = username if name.lower() == username else f"{username} ({name})"
        user_id = username

    contributor_commits[user_id] += 1
    if user_id not in id_to_display:
        id_to_display[user_id] = display

# Append bot
if bot_count > 0:
    contributor_commits["bot"] = bot_count
    id_to_display["bot"] = "GitHub Actions [bot]"

# === DATA FOR PIE CHART ===
labels = [id_to_display[k] for k in contributor_commits]
sizes = list(contributor_commits.values())

# === SHADE GENERATOR BASED ON BRIGHTNESS ===
def is_dark(color_rgb):
    r, g, b = color_rgb
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    return brightness < 0.5

def generate_smart_shades(base_colors, total_needed):
    base_rgb = [np.array(mcolors.to_rgb(c)) for c in base_colors]
    output = []
    steps = (total_needed // len(base_rgb)) + 1

    for base in base_rgb:
        dark = is_dark(base)
        for i in range(steps):
            factor = 1 - (i * 0.12) if dark else 1 + (i * 0.12)
            shaded = tuple((base * factor).clip(0, 1))
            output.append(shaded)
            if len(output) == total_needed:
                return output
    return output[:total_needed]

# === COLOR HANDLING ===
if palette:
    pie_colors = generate_smart_shades(palette, len(labels))
else:
    pie_colors = plt.get_cmap("tab20c").colors[:len(labels)]

# === PLOT PIE ===
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

plt.legend(wedges, labels, title="Contributors", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
plt.axis("equal")
plt.title("Contributions by Commits", fontsize=16, fontweight='bold')
plt.savefig("contributor-pie.png", bbox_inches="tight")
plt.show()
