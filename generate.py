import subprocess
import matplotlib.pyplot as plt
import sys
from collections import defaultdict, Counter
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

# === UNIFY CONTRIBUTORS BY USERNAME ===
user_commits = defaultdict(int)
email_to_username = {}

for line in lines:
    try:
        name, email = line.split("||")
    except ValueError:
        continue

    if "github-actions[bot]" in name:
        user_commits["github-actions[bot]"] += 1
        continue

    # Try to extract GitHub username from noreply email
    match = re.match(r"(\d+)?\+?([^@]+)@users\.noreply\.github\.com", email)
    if match:
        username = match.group(2).lower()
    else:
        username = re.sub(r"\s+", "", name).lower()  # fallback to name without spaces

    user_commits[username] += 1

# === PREPARE DATA ===
labels = list(user_commits.keys())
sizes = list(user_commits.values())

# === DETERMINE IF COLOR IS DARK ===
def is_dark(rgb):
    r, g, b = rgb
    brightness = (r*299 + g*587 + b*114) / 1000  # luminance formula
    return brightness < 0.5

# === GENERATE SHADED COLORS ===
def generate_smart_shades(base_colors, total):
    base_rgb = [np.array(mcolors.to_rgb(c)) for c in base_colors]
    output = []
    shade_steps = (total // len(base_rgb)) + 1

    for base in base_rgb:
        dark = is_dark(base)
        for i in range(shade_steps):
            # Adjust brightness toward white if dark, or toward black if light
            factor = 1 + (i * 0.15) if dark else 1 - (i * 0.15)
            adjusted = (base * factor).clip(0, 1)
            output.append(adjusted)
            if len(output) == total:
                return output
    return output[:total]

# === SET FINAL COLORS ===
if palette:
    pie_colors = generate_smart_shades(palette, len(labels))
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

plt.legend(wedges, labels, title="Contributors", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
plt.axis("equal")
plt.title("Contributions by Commits", fontsize=16, fontweight='bold')
plt.savefig("contributor-pie.png", bbox_inches="tight")
plt.show()
