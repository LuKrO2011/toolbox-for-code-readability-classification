import matplotlib.pyplot as plt
import numpy as np

from readability_preprocessing.evaluation.utils import load_repos

data = load_repos(top_k=10)

# Extract the statistics for each repository
repo_names = []
forks = []
stars = []
watchers = []

for repo_info in data.values():
    repo_names.append(repo_info.get('name'))
    forks.append(repo_info.get('forks', 0))
    stars.append(repo_info.get('stargazers_count', 0))
    watchers.append(repo_info.get('watchers_count', 0))

# Set the width of the bars
bar_width = 0.25

# Set position of bars on X axis
r1 = np.arange(len(repo_names))
r2 = [x + bar_width for x in r1]
r3 = [x + bar_width for x in r2]

# Create bar plots for forks, stars, and watchers
plt.figure(figsize=(12, 6))

plt.bar(r1, forks, color='b', width=bar_width, edgecolor='grey', label='Forks')
plt.bar(r2, stars, color='g', width=bar_width, edgecolor='grey', label='Stars')
plt.bar(r3, watchers, color='r', width=bar_width, edgecolor='grey', label='Watchers')

plt.xlabel('Repositories')
plt.ylabel('Count')
plt.title('Forks, Stars, and Watchers of Repositories')
plt.xticks([r + bar_width for r in range(len(repo_names))], repo_names,
           rotation='vertical')
plt.legend()

plt.tight_layout()
plt.show()
