import subprocess
import matplotlib.pyplot as plt
import sys
from collections import Counter
import re

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
    colors = palette[:len(labels)]
else:
    colors = plt.get_cmap("tab20c").colors[:len(labels)]

plt.figure(figsize=(width, height))
plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
plt.axis("equal")
plt.title("Contributions by Commits")
plt.savefig("contributor-pie.png")
