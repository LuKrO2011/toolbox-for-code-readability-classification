from pathlib import Path

from readability_preprocessing.utils.utils import list_java_files

input_path = Path("D:/PyCharm_Projects_D/styler2.0/Umfrage/part1")
java_files = list_java_files(str(input_path))

# Example name: 8_stratum3_newlinesFew_hbase_MultiByteBuff.java

# Split the name into its parts
cleaned_names = []
for filename in java_files:
    # Remove everything before the last \\
    filename = filename.split("\\")[-1]

    parts = filename.split("_")

    # Remove the first three parts
    parts = parts[2:]

    # Concat the remaining parts
    variant = parts[0]
    name = "_".join(parts[1:])

    cleaned_names.append((variant, name))

# Count the occurrences of each name
name_counts = {}
for variant, name in cleaned_names:
    if name in name_counts:
        name_counts[name] += 1
    else:
        name_counts[name] = 1

print(name_counts)

# Check if all counts are 10
all_counts_are_10 = True
for name, count in name_counts.items():
    if count != 10:
        all_counts_are_10 = False
        print(name, count)

print("All counts are 10:", all_counts_are_10)

# Count the occurrences of each variant for each name
name_variant_counts = {}
for variant, name in cleaned_names:
    if name not in name_variant_counts:
        name_variant_counts[name] = {}

for variant, name in cleaned_names:
    if name in name_variant_counts and variant in name_variant_counts[name]:
        name_variant_counts[name][variant] += 1
    else:
        name_variant_counts[name][variant] = 1

print(name_variant_counts)

# Check if all counts are 1
all_counts_are_1 = True
for name, variants in name_variant_counts.items():
    for variant, count in variants.items():
        if count != 1:
            all_counts_are_1 = False
            print(name, variant, count)

print("All counts are 1:", all_counts_are_1)

# SINGLE SHEET

num_sheets = 10
for i in range(num_sheets):
    sheet_name = f"sheet_{i}"
    input_path = Path("D:/PyCharm_Projects_D/styler2.0/Umfrage/part1/" + sheet_name)
    java_files = list_java_files(str(input_path))
    print()
    print(sheet_name)

    # Split the name into its parts
    cleaned_names = []
    for filename in java_files:
        # Remove everything before the last \\
        filename = filename.split("\\")[-1]

        parts = filename.split("_")

        # Remove the first three parts
        parts = parts[2:]

        # Concat the remaining parts
        variant = parts[0]
        name = "_".join(parts[1:])

        cleaned_names.append((variant, name))

    # Count the occurrences of each name
    name_counts = {}
    for variant, name in cleaned_names:
        if name in name_counts:
            name_counts[name] += 1
        else:
            name_counts[name] = 1

    print(name_counts)

    # Check if all counts are 1
    all_counts_are_1 = True
    for name, count in name_counts.items():
        if count != 1:
            all_counts_are_1 = False
            print(name, count)

    print("All counts are 1:", all_counts_are_1)
