import requests
import matplotlib.pyplot as plt
import sys
import numpy as np
import requests
import colorsys
from matplotlib import colors as mcolors

# === INPUTS ===
chart_size = sys.argv[1] if len(sys.argv) > 1 else '6,6'
width, height = map(int, chart_size.split(','))
palette = [c.strip() for c in sys.argv[2].split(',')] if len(sys.argv) > 2 else ['#EBE8DB', '#D76C82', '#B03052', '#3D0301']
repo_url = sys.argv[3] if len(sys.argv) > 3 else None

# Check if the repository URL is provided
if not repo_url:
    print("Error: No repository URL provided. Please provide the repository URL as the 3rd argument.")
    sys.exit(1)


# === GATHER CONTRIBUTORS FROM GITHUB API ===
response = requests.get(repo_url)
contributors_data = response.json()

# === PROCESS CONTRIBUTORS ===
contributor_commits = {}
display_name_map = {}
bot_count = 0

for contributor in contributors_data:
    username = contributor["login"]
    commit_count = contributor["contributions"]
    
    # Skip bot contributions
    if "bot" in username.lower():
        bot_count += 1
        continue

    display_name_map[username] = username
    contributor_commits[username] = commit_count

# Add bot with a neutral gray color
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

# Generate the colors for the contributors
pie_colors = generate_distinct_colors(palette, len(labels) - 1) + [(0.6, 0.6, 0.6)]  
pie_colors = pie_colors[:len(labels)] 

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
