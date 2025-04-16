import subprocess
import matplotlib.pyplot as plt
import sys
from collections import defaultdict
import re
import numpy as np
import colorsys
from matplotlib import colors as mcolors

# === INPUTS ===
chart_size = sys.argv[1] if len(sys.argv) > 1 else '6,6'
width, height = map(int, chart_size.split(','))
palette = [c.strip() for c in sys.argv[2].split(',')] if len(sys.argv) > 2 else ['#0A122A', '#698F3F', '#E7DECD', '#FBFAF8', '#F8F6F1']

# === GATHER GIT LOG DATA ===
log_output = subprocess.check_output(["git", "log", "--pretty=format:%an||%ae"]).decode("utf-8")
lines = log_output.strip().split("\n")

# === PROCESS CONTRIBUTORS ===
contributor_commits = defaultdict(int)
display_name_map = {}
bot_count = 0

for line in lines:
    try:
        name, email = line.split("||")
    except ValueError:
        continue

    name = name.strip()
    email = email.strip().lower()

    if "github-actions[bot]" in name:
        bot_count += 1
        continue

    # GitHub noreply -> get username
    match = re.match(r"([a-zA-Z0-9\-]+)@users\.noreply\.github\.com", email)
    if match:
        username = match.group(1).lower()
        display = f"{username} ({name})" if username != name.lower() else username
        user_id = username
    else:
        # Normal email, unify based on lowercased email
        username = re.sub(r'\s+', '', name.lower())
        user_id = email
        display = username if username == name.lower() else f"{username} ({name})"

    if user_id not in display_name_map:
        display_name_map[user_id] = display

    contributor_commits[user_id] += 1

if bot_count > 0:
    contributor_commits["__bot__"] = bot_count
    display_name_map["__bot__"] = "github-actions[bot]"

# === ORDER CONTRIBUTORS ===
contributors = list(contributor_commits.items())
# Move bot to end
contributors.sort(key=lambda x: (x[0] == '__bot__', -x[1]))

labels = [display_name_map[user_id] for user_id, _ in contributors]
sizes = [commit_count for _, commit_count in contributors]

# === GENERATE DISTINCT COLORS ===
def generate_distinct_colors(base_colors, total_needed):
    base_rgb = [np.array(mcolors.to_rgb(c)) for c in base_colors]
    result = []
    shade_steps = (total_needed // len(base_rgb)) + 1

    for base in base_rgb:
        r, g, b = base
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        for step in range(shade_steps):
            hue_shift = (step * 0.11) % 1.0
            light_adjust = (0.4 + 0.6 * ((step + 1) / shade_steps)) if l < 0.5 else (1.0 - 0.5 * ((step + 1) / shade_steps))
            new_h = (h + hue_shift) % 1.0
            new_l = max(0.15, min(0.95, light_adjust))
            new_s = min(1.0, s * 1.1)

            new_rgb = colorsys.hls_to_rgb(new_h, new_l, new_s)
            result.append(new_rgb)

            if len(result) == total_needed:
                return result
    return result[:total_needed]

# Add bot with a neutral gray color
pie_colors = generate_distinct_colors(palette, len(labels) - 1) + [(0.6, 0.6, 0.6)]  # Neutral gray for bot
pie_colors = pie_colors[:len(labels)]  # Ensure it matches the number of labels

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

# Add bot to the legend at the end
labels.append("github-actions[bot]")
plt.legend(wedges, labels, title="Contributors", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
plt.axis("equal")
plt.title("Contributions by Commits", fontsize=16, fontweight='bold')
plt.savefig("contributor-pie.png", bbox_inches="tight")
plt.show()
