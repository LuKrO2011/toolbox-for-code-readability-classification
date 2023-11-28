from readability_preprocessing.evaluation.utils import load_repos, PROJECT_DIR

OUTPUT_NAME = PROJECT_DIR / "repository_statistics.tex"

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

# Create the LaTeX table content
latex_table = "\\begin{tabular}{|c|c|c|c|}\n"
latex_table += "\\hline\n"
latex_table += "Repository & Forks & Stars & Watchers \\\\\n"
latex_table += "\\hline\n"

for i in range(len(repo_names)):
    latex_table += f"{repo_names[i]} & {forks[i]} & {stars[i]} & {watchers[i]} \\\\\n"

latex_table += "\\hline\n"
latex_table += "\\end{tabular}"

# Write the LaTeX table content to a .tex file
latex_file_path = OUTPUT_NAME
with open(latex_file_path, 'w') as latex_file:
    latex_file.write(latex_table)
