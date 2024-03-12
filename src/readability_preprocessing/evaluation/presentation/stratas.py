import matplotlib.pyplot as plt

# Data from the table
properties = ["Getters &\nSetters", "Other\nmethods"]
method_counts = [19016, 4280 + 78 + 15938]

# Plotting the pie chart
fig, ax = plt.subplots(figsize=(4, 3))
ax.pie(method_counts, labels=properties, autopct="%1.1f%%", startangle=90)

# Display the plot
plt.tight_layout()
plt.savefig("getters-setters.png", dpi=1000)
plt.show()

# Data from the table
properties = ["Easy\n(Getters &\nSetters)", "Complex", "", "Medium"]
method_counts = [19016, 4280, 78, 15938]

# Plotting the pie chart
fig, ax = plt.subplots(figsize=(4, 3))
ax.pie(
    method_counts,
    labels=properties,
    autopct=lambda p: "" if p < 5 else f"{p:.1f}%",
    startangle=90,
)

# Display the plot
plt.tight_layout()
plt.savefig("stratas.png", dpi=1000)
plt.show()
