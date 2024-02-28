import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.utils import load_repos

data = load_repos(top_k=10)

# Extract the statistics for forks, stars, and watchers
forks_data = [repo_info.get("forks", 0) for repo_info in data.values()]
stars_data = [repo_info.get("stargazers_count", 0) for repo_info in data.values()]
watchers_data = [repo_info.get("watchers_count", 0) for repo_info in data.values()]

# Create a box plot for forks, stars, and watchers
plt.figure(figsize=(8, 6))

plt.boxplot(
    [forks_data, stars_data, watchers_data], labels=["Forks", "Stars", "Watchers"]
)
plt.title("Box Plot of Forks, Stars, and Watchers")
plt.ylabel("Count")
plt.ylim(0, 45000)

plt.tight_layout()
plt.show()
