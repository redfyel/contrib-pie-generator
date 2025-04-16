import subprocess
import matplotlib.pyplot as plt
import sys
from collections import Counter
import re
import numpy as np
from matplotlib import colors as mcolors  # Avoid naming conflict with `colors` list

# --- Input handling ---
chart_size = sys.argv[1] if len(sys.argv) > 1 else '6,6'
width, height = map(int, chart_size.split(','))
palette = [c.strip() for c in sys.argv[2].split(',')] if len(sys.argv) > 2 else None

# --- Get git commit author data ---
log_output = subprocess.check_output(["git", "log", "--pretty=format:%an||%ae"]).decode("utf-8")
lines = log_output.strip().split("\n")

# --- Contributor mapping & count ---
name_map = {}
author_data = []
bot_count = 0

for line in lines:
    try:
        name, email = line.split("||")
    except ValueError:
        name = line
        email = ""

    # Detect GitHub Actions bot
    if "github-actions[bot]" in name:
        bot_count += 1
        continue

    match = re.match(r"(.*)@users\.noreply\.github\.com", email)
    if match:
        username = match.group(1)
        # Merge aliases: if name != username, treat them as one
        key = username.lower()
        display = f"{name} ({username})" if name.lower() != username.lower() else username
    else:
        key = name.lower()
        display = name

    name_map[key] = display
    author_data.append(key)

# Count and resolve display names
author_counts = Counter(author_data)
labels = [name_map[k] for k in author_counts.keys()]
sizes = list(author_counts.values())

# Append bot at the end
if bot_count > 0:
    labels.append("GitHub Actions [bot]")
    sizes.append(bot_count)

# --- Generate distinct shades from base palette ---
def generate_shades(base_colors, total):
    output = []
    steps = max(1, total // len(base_colors) + 1)
    for i, base in enumerate(base_colors):
        base_rgb = np.array(mcolors.to_rgb(base))
        for j in range(steps):
            factor = 1 - (j / (steps * 1.5))  # Slightly darker each step
            shaded = tuple((base_rgb * factor).clip(0, 1))
            output.append(shaded)
            if len(output) == total:
                return output
    return output[:total]

if palette:
    pie_colors = generate_shades(palette, len(labels))
else:
    cmap = plt.get_cmap("tab20c")
    pie_colors = cmap.colors[:len(labels)]

# --- Plotting ---
plt.figure(figsize=(width, height))
wedges, texts, autotexts = plt.pie(
    sizes,
    labels=None,  # Remove inline labels
    colors=pie_colors,
    autopct="%1.1f%%",
    startangle=140,
    textprops={'color': 'white', 'fontsize': 12},
    wedgeprops={'edgecolor': 'black', 'linewidth': 1, 'linestyle': 'solid'}
)

# Legend with names
plt.legend(wedges, labels, title="Contributors", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)

plt.axis("equal")
plt.title("Contributions by Commits", fontsize=14, fontweight='bold')
plt.savefig("contributor-pie.png", bbox_inches="tight")
plt.show()
