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

# === MERGE CONTRIBUTORS ===
email_to_id = {}
id_to_display = {}
contributor_commits = defaultdict(int)
bot_count = 0

for line in lines:
    try:
        name, email = line.split("||")
    except ValueError:
        continue

    if "github-actions[bot]" in name:
        bot_count += 1
        continue

    # If noreply GitHub email, extract username
    match = re.match(r"(.*)@users\.noreply\.github\.com", email)
    if match:
        username = match.group(1).lower()
        user_id = username  # Unify based on GitHub username
        display = f"{name} ({username})" if name.lower() != username else username
    else:
        user_id = email.lower()
        display = name

    # Assign only the first encountered display name for consistency
    if user_id not in id_to_display:
        id_to_display[user_id] = display

    contributor_commits[user_id] += 1

# === APPEND BOT ===
if bot_count > 0:
    contributor_commits["bot"] = bot_count
    id_to_display["bot"] = "GitHub Actions [bot]"

# === PREPARE DATA FOR CHART ===
labels = [id_to_display[k] for k in contributor_commits.keys()]
sizes = list(contributor_commits.values())

# === SMART SHADE GENERATOR ===
def generate_distinct_colors(base_colors, total):
    base_rgb = [np.array(mcolors.to_rgb(c)) for c in base_colors]
    output = []
    shade_steps = (total // len(base_rgb)) + 1

    for base in base_rgb:
        for i in range(shade_steps):
            factor = 1 - (i * 0.15)
            shaded = tuple((base * factor).clip(0, 1))
            output.append(shaded)
            if len(output) == total:
                return output
    return output[:total]

if palette:
    pie_colors = generate_distinct_colors(palette, len(labels))
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
