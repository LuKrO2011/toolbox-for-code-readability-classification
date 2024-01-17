import os
import shutil

import numpy as np

from readability_preprocessing.utils.utils import list_non_hidden

default_strata_distributions = {
    "stratum_0": 0.2,
    "stratum_1": 0.4,
    "stratum_2": 0.1,
    "stratum_3": 0.3,
}

default_rdh_distributions = {
    "all": 0.0,
    "all_weak": 0.0,
    "all_weak_2": 0.0,
    "all_weak_3": 0.0,
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


class Snippet:
    """
    A snippet is a code snippet. It belongs to a RDH.
    """

    def __init__(self, name: str):
        """
        Initialize the snippet.
        :param name:
        """
        self.stratum = None
        self.rdh = None
        self.name = name

    def set_rdh(self, rdh):
        """
        Set the rdh the snippet belongs to.
        :param rdh: The rdh the snippet belongs to.
        :return: None
        """
        self.rdh = rdh

    def set_stratum(self, stratum):
        """
        Set the stratum the snippet belongs to.
        :param stratum: The stratum the snippet belongs to.
        :return: None
        """
        self.stratum = stratum


class RDH:
    """
    A RDH is one readability-decreasing-heuristic variant generated by a single config.
    A RDH belongs to a stratum.
    """

    def __init__(self, name: str, probability: float, unused_snippets: list[Snippet]):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        :param probability: The probability of the RDH for sampling.
        :param unused_snippets: The list of unused snippets.
        """
        self.name = name
        self.probability = probability
        self.unused_snippets = unused_snippets
        for snippet in unused_snippets:
            snippet.set_rdh(self)
        self.stratum = None

    def set_stratum(self, stratum):
        """
        Set the stratum the RDH belongs to.
        :param stratum: The stratum the RDH belongs to.
        :return: None
        """
        self.stratum = stratum


class Stratum:
    """
    A stratum is a group of RDHs that are similar according to the stratified sampling.
    """

    def __init__(self, name: str, probability: float, rdhs: list[RDH]):
        """
        Initialize the stratum.
        :param name: The name of the stratum.
        :param probability: The probability of the stratum for sampling.
        :param rdhs: The list of RDHs.
        """
        self.name = name
        self.probability = probability
        self.rdhs = rdhs
        for rdh in rdhs:
            rdh.set_stratum(self)
            for snippet in rdh.unused_snippets:
                snippet.set_stratum(self)


class Survey:
    """
    A survey contains a list of snippets.
    """

    def __init__(self, snippets):
        """
        Initialize the survey.
        :param snippets: The list of snippets belonging to the survey.
        """
        self.snippets = snippets


def _fix_probabilities(probabilities: list[float]) -> list[float]:
    """
    Fix the probabilities so that they sum to 1 by adding the difference equally
    to all probabilities. This might be necessary after deleting one or more strata or
    rdh.
    :param probabilities: The probabilities to fix.
    :return: The fixed probabilities.
    """
    if sum(probabilities) != 1:
        difference = 1 - sum(probabilities)
        probabilities = [p + difference / len(probabilities) for p in probabilities]
    return probabilities


def _select_stratum(strata: list[Stratum]) -> Stratum:
    """
    Select a stratum according to the probabilities.
    :param strata: The list of strata to select from.
    :return: The selected stratum.
    """
    stratum_probabilities = [stratum.probability for stratum in strata]
    stratum_probabilities = _fix_probabilities(stratum_probabilities)
    stratum = np.random.choice(strata, p=stratum_probabilities)
    return stratum


def _select_rdh(rdhs: list[RDH]) -> RDH:
    """
    Select a rdh according to the probabilities.
    :param rdhs: The list of rdhs to select from.
    :return: The selected rdh.
    """
    rdh_probabilities = [rdh.probability for rdh in rdhs]
    rdh_probabilities = _fix_probabilities(rdh_probabilities)
    rdh = np.random.choice(rdhs, p=rdh_probabilities)
    return rdh


def _select_snippet(snippets: list[Snippet]) -> Snippet:
    """
    Select a snippet according to the probabilities.
    :param snippets: The list of snippets to select from.
    :return: The selected snippet.
    """
    snippet_probabilities = [1 / len(snippets) for _ in snippets]
    snippet = np.random.choice(snippets, p=snippet_probabilities)
    return snippet


class SurveyCrafter:
    """
    A class for crafting surveys from the given input directory and save them to the
    given output directory.
    """

    def __init__(self, input_dir: str,
                 output_dir: str,
                 snippets_per_sheet: int = 20,
                 num_sheets: int = 20,
                 strata_distributions: dict[str, float] = None,
                 rdh_distributions: dict[str, float] = None):
        """
        Initialize the survey crafter.
        :param input_dir: The input directory with the stratas, rdhs and snippets.
        :param output_dir: The output directory to save the surveys to.
        :param snippets_per_sheet: How many snippets per sheet.
        :param num_sheets: How many sheets.
        :param strata_distributions: The strata distributions.
        :param rdh_distributions: The rdh distributions.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.snippets_per_sheet = snippets_per_sheet
        self.num_sheets = num_sheets
        self.strata_distributions = (strata_distributions or
                                     default_strata_distributions.copy())
        self.rdh_distributions = rdh_distributions or default_rdh_distributions.copy()

    def craft_surveys(self) -> None:
        """
        Craft surveys from the given input directory and save them to the given
        output directory.
        :return: None
        """
        strata = self.craft_stratas()
        surveys = self.sample_sheets(strata)
        self._write_output(surveys)

    def craft_stratas(self) -> list[Stratum]:
        """
        Craft the stratas from the input directory.
        :return: The stratas.
        """
        # Load the stratas and rdhs
        strata_names, strata_probabilities = self._load_stratas()
        rdh_names, rdh_probabilities = self._load_rdhs(strata_names)

        # Convert the strats and rdhs to objects with probabilities
        # If no probability is specified, the probability is 0
        strata = []
        for strata_name, strata_probability in zip(strata_names, strata_probabilities):
            rdhs = []
            for rdh_name, rdh_probability in zip(rdh_names[strata_name],
                                                 rdh_probabilities[strata_name]):
                unused_snippet_names = list_non_hidden(
                    os.path.join(self.input_dir, strata_name, rdh_name))
                unused_snippets = [Snippet(snippet_name) for snippet_name in
                                   unused_snippet_names]
                rdhs.append(RDH(rdh_name, rdh_probability, unused_snippets))
            strata.append(Stratum(strata_name, strata_probability, rdhs))

        # Remove empty rdhs and stratas
        for stratum in strata:
            stratum.rdhs = [rdh for rdh in stratum.rdhs if len(rdh.unused_snippets) > 0]
        strata = [stratum for stratum in strata if len(stratum.rdhs) > 0]

        return strata

    def _load_rdhs(self, strata_names: list[str]) -> tuple[dict[str, list[str]],
    dict[str, list[float]]]:
        """
        Load the rdhs from the input directory.
        :param strata_names: The names of the stratas.
        :return: The rdh names and probabilities.
        """
        # Load the rdh names as the names of the subdirectories
        rdh_names = {}
        for strata_name in strata_names:
            rdh_names[strata_name] = list_non_hidden(os.path.join(self.input_dir,
                                                                  strata_name))

        # Assign each rdh a probability distribution
        rdh_probabilities = {}
        for strata_name in strata_names:
            rdh_probabilities[strata_name] = []
            for rdh_name in rdh_names[strata_name]:
                rdh_probabilities[strata_name].append(
                    self.rdh_distributions[rdh_name])

        return rdh_names, rdh_probabilities

    def _load_stratas(self) -> tuple[list[str], list[float]]:
        """
        Load the stratas from the input directory.
        :return: The strata names and probabilities.
        """
        # Load the strata names as the names of the subdirectories
        strata_names = list_non_hidden(self.input_dir)

        # Assign each stratum a probability distribution
        strata_probabilities = []
        for strata_name in strata_names:
            strata_probabilities.append(self.strata_distributions[strata_name])

        return strata_names, strata_probabilities

    def _write_output(self, surveys: list[Survey]) -> None:
        """
        Write the output to the output directory.
        :param surveys: The surveys to write to the output directory.
        :return: The surveys.
        """
        # Create num_sheets output subdirectories
        for i in range(self.num_sheets):
            os.makedirs(os.path.join(self.output_dir, f"sheet_{i}"), exist_ok=True)

        # Copy the snippets to the output subdirectories with name "stratum_rdh_oldName"
        for i, survey in enumerate(surveys):
            for j, snippet in enumerate(survey.snippets):
                stratum = snippet.stratum.name
                rdh = snippet.rdh.name
                old_name = snippet.name
                new_name = f"{stratum}_{rdh}_{old_name}"
                shutil.copy(
                    os.path.join(self.input_dir, stratum, rdh, old_name),
                    os.path.join(self.output_dir, f"sheet_{i}", new_name),
                )

    def sample_sheets(self, strata: list[Stratum]) -> list[Survey]:
        """
        Sample the surveys.
        :param strata: The strata to sample from.
        :return: The sampled surveys.
        """
        # Create num_sheet surveys with different snippets according to the probs
        surveys = []
        for i in range(self.num_sheets):
            snippets = []
            for j in range(self.snippets_per_sheet):

                # Select a stratum, a rdh and a snippet
                stratum = _select_stratum(strata)
                rdh = _select_rdh(stratum.rdhs)
                snippet = _select_snippet(rdh.unused_snippets)

                # Add the snippet to the list of snippets
                snippets.append(snippet)
                rdh.unused_snippets.remove(snippet)

                # Remove the rdh or stratum if there are no more snippets
                self._clean_up(rdh, strata, stratum)

                # If there are no more strata, stop
                if len(strata) == 0:
                    break

            # Add the survey to the list of surveys
            surveys.append(Survey(snippets))

            # If there are no more strata, stop
            if len(strata) == 0:
                break

        return surveys

    @staticmethod
    def _clean_up(rdh: RDH, strata: list[Stratum], stratum: Stratum) -> None:
        """
        Clean up the rdh and stratum if there are no more snippets.
        :param rdh: The rdh to clean up.
        :param strata: The strata to clean up.
        :param stratum: The stratum to clean up.
        :return: None
        """
        # If it was the last snippet, remove the rdh
        if len(rdh.unused_snippets) == 0:
            stratum.rdhs.remove(rdh)

        # If it was the last rdh, remove the stratum
        if len(stratum.rdhs) == 0:
            strata.remove(stratum)
