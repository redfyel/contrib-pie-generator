import subprocess
import matplotlib.pyplot as plt
import sys
from collections import Counter
import re
import numpy as np

# Accept chart size from the input (format: "width,height")
chart_size = sys.argv[1] if len(sys.argv) > 1 else '6,6'
width, height = map(int, chart_size.split(','))

# Optional: Accept a custom palette as a comma-separated list of colors.
palette = None
if len(sys.argv) > 2:
    # Split by comma and remove any extra whitespace from each color string.
    palette = [c.strip() for c in sys.argv[2].split(',')]

# Use git log to get both author name and email in the format "name||email"
log_output = subprocess.check_output(["git", "log", "--pretty=format:%an||%ae"]).decode("utf-8")
lines = log_output.strip().split("\n")

# Process each line to filter out bot commits and combine name and username if available.
author_data = []
for line in lines:
    try:
        name, email = line.split("||")
    except ValueError:
        name = line
        email = ""
    
    # Filter out bot commits.
    if "github-actions[bot]" in name:
        continue

    # Extract the username if the email matches GitHub's noreply pattern.
    match = re.match(r"(.*)@users\.noreply\.github\.com", email)
    if match:
        username = match.group(1)
        if name.strip().lower() != username.strip().lower():
            label = f"{name} ({username})"
        else:
            label = name
    else:
        label = name

    author_data.append(label)

author_counts = Counter(author_data)
labels = list(author_counts.keys())
sizes = list(author_counts.values())

# Use the custom palette if provided; otherwise, use Matplotlib's default "tab20c".
if palette:
    # Generate lighter shades from the palette for better contrast
    colors = [np.array(plt.colors.hex2color(c)) * 0.7 for c in palette[:len(labels)]]
else:
    colors = plt.get_cmap("tab20c").colors[:len(labels)]

# Create a pie chart with rounded edges
plt.figure(figsize=(width, height))

# Create pie chart with shadows and white text for better contrast
wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140, 
                                   textprops={'color': 'white', 'fontsize': 12}, wedgeprops={'edgecolor': 'black', 'linewidth': 1, 'linestyle': 'solid'})

# Add a legend on the side of the pie chart
plt.legend(wedges, labels, title="Contributors", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)

# Add a shadow effect to the pie chart
plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title("Contributions by Commits", fontsize=14, fontweight='bold')

# Save the updated pie chart
plt.savefig("contributor-pie.png", bbox_inches="tight")
plt.show()
