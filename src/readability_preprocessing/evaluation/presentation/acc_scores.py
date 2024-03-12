import matplotlib.pyplot as plt

# Data from the table
configurations = [
    "model paper",
    "merged-merged",
    "mam-mam",
    "mam-merged",
    "merged-mam",
    "finetune",
]
accuracy_values = [85.3, 84.7, 92.2, 61.9, 56.8, 83.3]

# Plotting the bar chart
fig, ax = plt.subplots(figsize=(4, 3))
bars = ax.bar(range(len(configurations)), accuracy_values)
plt.ylabel("Accuracy (%)")
plt.ylim(0, 100)
plt.xticks([])

# Display the configuration names inside the bars
for bar, config, acc in zip(bars, configurations, accuracy_values, strict=False):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() / 2,
        config,
        ha="center",
        va="center",
        color="white",
        fontweight="bold",
        rotation=90,
    )
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{acc:.1f}%",
        ha="center",
        va="bottom",
    )

# Show the plot
plt.tight_layout()
plt.savefig("acc_scores.png", dpi=1000)
plt.show()
