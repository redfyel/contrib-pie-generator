import subprocess
import matplotlib.pyplot as plt
from collections import Counter

log_output = subprocess.check_output(["git", "log", "--pretty=format:%an"]).decode("utf-8")
authors = log_output.strip().split("\n")
author_counts = Counter(authors)

labels = list(author_counts.keys())
sizes = list(author_counts.values())
colors = plt.get_cmap("tab20c").colors

plt.figure(figsize=(6, 6))
plt.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct="%1.1f%%", startangle=140)
plt.axis("equal")
plt.title("Contributions by Commits")
plt.savefig("contributor-pie.png")
