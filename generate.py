import subprocess
import matplotlib.pyplot as plt
import sys
from collections import Counter

# Accept chart size from the input
chart_size = sys.argv[1] if len(sys.argv) > 1 else '6,6'
width, height = map(int, chart_size.split(','))

log_output = subprocess.check_output(["git", "log", "--pretty=format:%an"]).decode("utf-8")
authors = log_output.strip().split("\n")
author_counts = Counter(authors)

labels = list(author_counts.keys())
sizes = list(author_counts.values())
colors = plt.get_cmap("tab20c").colors

plt.figure(figsize=(width, height))
plt.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct="%1.1f%%", startangle=140)
plt.axis("equal")
plt.title("Contributions by Commits")
plt.savefig("contributor-pie.png")
