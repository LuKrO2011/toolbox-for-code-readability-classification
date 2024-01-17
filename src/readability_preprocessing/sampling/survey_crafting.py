import os
import shutil

import numpy as np

strata_distributions = {
    "stratum_0": 0.2,
    "stratum_1": 0.4,
    "stratum_2": 0.1,
    "stratum_3": 0.3,
}

rdh_distributions = {
    "all": 0.0,
    "all_weak": 0.0,
    "all_weak2": 0.0,
    "all_weak3": 0.0,
    "comments_remove": 0.06,
    "methods": 0.4,
    "misc": 0.06,
    "newlines_few": 0.06,
    "newlines_many": 0.06,
    "realistic": 0.06,
    "rename": 0.06,
    "spaces_few": 0.06,
    "spaces_many": 0.06,
    "tabs_few": 0.06,
    "tabs_many": 0.06,
}


class RDH:
    def __init__(self, name, probability, snippets):
        self.name = name
        self.probability = probability
        self.snippets = snippets


class Stratum:
    def __init__(self, name, probability, rdhs):
        self.name = name
        self.probability = probability
        self.rdhs = rdhs


class Snippet:
    def __init__(self, stratum, rdh, name):
        self.stratum = stratum
        self.rdh = rdh
        self.name = name


class Survey:
    def __init__(self, snippets):
        self.snippets = snippets


def select_stratum(strata):
    # Select a stratum according to the probabilities
    stratum_probabilities = [stratum.probability for stratum in strata]
    stratum = np.random.choice(strata, p=stratum_probabilities)
    return stratum


def select_rdh(rdhs):
    # Select a rdh according to the probabilities
    rdh_probabilities = [rdh.probability for rdh in rdhs]
    rdh = np.random.choice(rdhs, p=rdh_probabilities)
    return rdh


def select_snippet(snippets, used_snippets):
    # Select a snippet according to the probabilities that has not been used yet
    snippet_probabilities = [1 / len(snippets) for snippet in snippets]
    snippet = np.random.choice(snippets, p=snippet_probabilities)
    while snippet in used_snippets:
        snippet = np.random.choice(snippets, p=snippet_probabilities)
    return snippet


def craft_surveys(input_dir, output_dir, snippets_per_sheet=20, num_sheets=20):
    # Load the strata names as the names of the subdirectories
    strata_names = os.listdir(input_dir)

    # Assign each stratum a probability distribution
    strata_probabilities = []
    for strata_name in strata_names:
        strata_probabilities.append(strata_distributions[strata_name])

    # Load the rdh names as the subdirectories of each stratum
    rdh_names = {}
    for strata_name in strata_names:
        rdh_names[strata_name] = os.listdir(os.path.join(input_dir, strata_name))

    # Convert the strats and rdhs to objects with probabilities
    # If no probability is specified, the probability is 0
    strata = []
    for strata_name, strata_probability in zip(strata_names, strata_probabilities):
        rdhs = []
        for rdh_name in rdh_names[strata_name]:
            rdhs.append(
                RDH(
                    name=rdh_name,
                    probability=rdh_distributions[rdh_name],
                    snippets=os.listdir(os.path.join(input_dir, strata_name, rdh_name)),
                )
            )
        strata.append(
            Stratum(name=strata_name, probability=strata_probability, rdhs=rdhs))

    # Create num_sheet surveys with different snippets according to the probabilities
    surveys = []
    used_snippets = []
    for i in range(num_sheets):
        snippets = []
        for j in range(snippets_per_sheet):
            # Select a stratum according to the probabilities
            stratum = select_stratum(strata)

            # Select a rdh according to the probabilities
            rdh = select_rdh(stratum.rdhs)

            # Select a snippet according to the probabilities
            snippet = select_snippet(rdh.snippets, used_snippets)

            # Add the snippet to the list of snippets
            snippets.append(snippet)

            # Add the snippet to the list of used snippets
            used_snippets.append(snippet)

        # Add the survey to the list of surveys
        surveys.append(Survey(snippets))

    # Create num_sheets output subdirectories
    for i in range(num_sheets):
        os.makedirs(os.path.join(output_dir, f"sheet_{i}"), exist_ok=True)

    # Copy the snippets to the output subdirectories
    # The new names are stratum_rdh_oldName
    for i, survey in enumerate(surveys):
        for j, snippet in enumerate(survey.snippets):
            stratum = snippet.split("_")[0]
            rdh = snippet.split("_")[1]
            old_name = snippet.split("_")[2]
            new_name = f"{stratum}_{rdh}_{old_name}"
            shutil.copy(
                os.path.join(input_dir, stratum, rdh, old_name),
                os.path.join(output_dir, f"sheet_{i}", new_name),
            )
