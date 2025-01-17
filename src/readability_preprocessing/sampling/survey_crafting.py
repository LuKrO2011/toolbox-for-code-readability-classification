import logging
import os
import random
import shutil
from pathlib import Path

import numpy as np

from readability_preprocessing.extractors.diff_extractor import compare_java_files
from readability_preprocessing.utils.utils import (
    list_non_hidden,
    load_txt_file,
    load_yaml_file,
)

default_sample_amount: dict[str, int] = {
    "stratum0": 2,
    "stratum1": 8,
    "stratum2": 2,
    "stratum3": 8,
}


def permutation_matrix(start_idx: int, matrix_size: int) -> np.ndarray:
    """
    Create a permutation matrix of the given size.
    :param start_idx: The index to start the permutation matrix at.
    :param matrix_size: The size of the permutation matrix.
    :return: The permutation matrix.
    """
    matrix = [
        [(i + start_idx, (i + j) % matrix_size) for j in range(matrix_size)]
        for i in range(matrix_size)
    ]

    # Transpose the matrix to get the desired output
    matrix = list(map(list, zip(*matrix, strict=True)))

    return np.array(matrix)


def permutation_matrix_2(
    start_idx: int, sub_matrix_size: int, width: int
) -> np.ndarray:
    """
    Create a permutation matrix of the given size. Therefore, multiple permutation
    matrices are combined.
    :param start_idx: The index to start the permutation matrix at.
    :param sub_matrix_size: The size of a sub matrix.
    :param width: The width of the combined permutation matrix.
    :return: The combined permutation matrix.
    """
    width_matrix_count = width // sub_matrix_size
    width_end_idx = start_idx + width_matrix_count
    sub_matrices = []
    for i in range(start_idx, width_end_idx):
        sub_matrices.append(
            permutation_matrix(
                start_idx=i * sub_matrix_size, matrix_size=sub_matrix_size
            )
        )
    return np.concatenate(sub_matrices, axis=1)


def permutation_matrix_3(sub_matrix_size: int, width: int, height: int) -> np.ndarray:
    """
    Create a permutation matrix of the given size. Therefore, multiple permutation
    matrices are combined.
    :param sub_matrix_size: The size of a sub matrix.
    :param width: The width of the combined permutation matrix.
    :param height: The height of the combined permutation matrix.
    :return: The combined permutation matrix.
    """
    height_matrix_count = height // sub_matrix_size
    sub_matrices = []
    for i in range(height_matrix_count):
        sub_matrices.append(
            permutation_matrix_2(
                start_idx=i * 2, sub_matrix_size=sub_matrix_size, width=width
            )
        )

    return np.concatenate(sub_matrices, axis=0)


# def permutation_matrix_3(sub_matrix_size: int, width: int, height: int) -> np.ndarray:
#     """
#     Create a permutation matrix of the given size. Therefore, multiple permutation
#     matrices are combined.
#     :param sub_matrix_size: The size of a sub matrix.
#     :param width: The width of the combined permutation matrix.
#     :param height: The height of the combined permutation matrix.
#     :return: The combined permutation matrix.
#     """
#     width_matrix_count = width // sub_matrix_size
#     height_matrix_count = height // sub_matrix_size
#     matrix_count = width_matrix_count * height_matrix_count
#     sub_matrices = []
#     for i in range(matrix_count):
#         sub_matrices.append(
#             permutation_matrix(
#                 start_idx=i * sub_matrix_size,
#                 matrix_size=sub_matrix_size))
#
#     # Concat 1 and 4 horizontally and 2 and 3 horizontally and then vertically
#     sub_matrices = [np.concatenate([sub_matrices[0], sub_matrices[3]], axis=1),
#                     np.concatenate([sub_matrices[1], sub_matrices[2]], axis=1)]
#     matrix = np.concatenate(sub_matrices, axis=0)
#     return matrix


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

    def get_path(self, root: Path) -> Path:
        """
        Get the path of the snippet.
        :return: The path of the snippet.
        """
        return root / self.stratum.name / self.rdh.name / self.name


class NoSnippet(Snippet):
    """
    An empty snippet that does not exist.
    """

    def __init__(self, name: str, rdh):
        """
        Initialize the empty snippet.
        """
        super().__init__(name)
        self.rdh = rdh

    def get_path(self, root: Path) -> None:
        """
        Get the path of the snippet.
        :return: The path of the snippet.
        """
        return


class RDH:
    """
    A RDH is one readability-decreasing-heuristic variant generated by a single config.
    A RDH belongs to a stratum.
    """

    def __init__(self, name: str, snippets: dict[str, Snippet]):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        :param snippets: The list of unused snippets.
        """
        self.name = name
        self.snippets = snippets
        for snippet in snippets.values():
            snippet.set_rdh(self)
        self.stratum = None

    def set_stratum(self, stratum):
        """
        Set the stratum the RDH belongs to.
        :param stratum: The stratum the RDH belongs to.
        :return: None
        """
        self.stratum = stratum

    def get_snippet(self, name: str) -> Snippet | None:
        """
        Get the snippet with the given name, if it exists.
        Otherwise, return NoSnippet.
        :param name: The name of the snippet.
        :return: The snippet or EmptySnippet.
        """
        if name in self.snippets:
            return self.snippets[name]

        logging.warning(f"Snippet {name} not found in rdh {self.name}.")
        return None


class Method:
    """
    A method combines an original snippet with a no modification snippet and a dict of
    rdh snippets. A method belongs to a stratum.
    """

    def __init__(self, original: Snippet, nomod: Snippet, rdhs: dict[str, Snippet]):
        """
        Initialize the method.
        :param original: The original snippet.
        :param nomod: The nomod snippet.
        :param rdhs: The rdh snippets.
        """
        self.stratum = None
        self.original = original
        self.nomod = nomod
        self.rdhs = rdhs

    def set_stratum(self, stratum):
        """
        Set the stratum the method belongs to.
        :param stratum: The stratum the method belongs to.
        :return: None
        """
        self.stratum = stratum
        self.original.set_stratum(stratum)
        self.nomod.set_stratum(stratum)
        for rdh in self.rdhs.values():
            rdh.set_stratum(stratum)

    def compare_to_nomod(self, root: Path) -> list[Snippet]:
        """
        Compare each rdh snippet to the nomod snippet and return the not-different
        snippets.
        :param root: The root directory.
        :return: The not-different snippets.
        """
        not_diff = []
        for rdh in self.rdhs.values():
            if not isinstance(rdh, NoSnippet):
                is_diff = compare_java_files(
                    self.nomod.get_path(root), rdh.get_path(root)
                )
                if not is_diff:
                    not_diff.append(rdh)
        return not_diff

    def pick_variant(self, variant: str) -> Snippet:
        """
        Obtain the variant of the method of the given variant.
        :param variant: The variant name or index.
        :return: The picked snippet.
        """
        if variant == "none":
            return self.nomod
        if variant == "methods":
            return self.original
        return self.rdhs[variant]


class Stratum:
    """
    A stratum is a group of RDHs that are similar according to the stratified sampling.
    """

    def __init__(self, name: str, methods: list[Method]):
        """
        Initialize the stratum.
        :param name: The name of the stratum.
        :param methods: The methods belonging to the stratum.
        """
        self.name = name
        self.methods = methods
        for method in self.methods:
            method.set_stratum(self)


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


class SurveyCrafter:
    """
    A class for crafting surveys from the given input directory and save them to the
    given output directory.
    """

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        snippets_per_sheet: int = 20,
        num_sheets: int = 10,
        sample_amount_path: Path = None,
        original_name: str = "methods",
        nomod_name: str = "none",
        exclude_path: Path = None,
    ):
        """
        Initialize the survey crafter.
        :param input_dir: The input directory with the stratas, rdhs and snippets.
        :param output_dir: The output directory to save the surveys to.
        :param snippets_per_sheet: How many snippets per sheet.
        :param sample_amount_path: The path to the sample amount file.
        :param num_sheets: How many sheets.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.snippets_per_sheet = snippets_per_sheet
        self.num_sheets = num_sheets
        self.original_name = original_name
        self.nomod_name = nomod_name
        self.num_stratas = None
        self.num_rdhs = None
        self.rdh_names = None
        self.int_to_key = None

        # Load the sample amount
        self.sample_amount: dict[str, float] = {}
        if sample_amount_path is not None:
            self.sample_amount = load_yaml_file(sample_amount_path)
        if self.sample_amount is None or len(self.sample_amount) == 0:
            self.sample_amount = default_sample_amount

        # Load the exclude list
        self.exclude: list[str] = []
        if exclude_path is not None:
            self.exclude = load_txt_file(exclude_path)

    def craft_surveys(self) -> None:
        """
        Craft surveys from the given input directory and save them to the given
        output directory.
        :return: None
        """
        strata = self.craft_stratas()

        # Log information about the stratas
        logging.info(f"Strata: Number of stratas: {len(strata)}")
        for stratum in strata.values():
            logging.info(f"{stratum.name}: Number of methods: {len(stratum.methods)}")

        methods = self.sample_methods(strata, sample_amount=self.sample_amount)

        # Store and log the original method name of each method
        self._store_methods(methods, "chosen_methods.txt")
        logging.info("Original method names of the sampled methods:")
        for method in methods:
            logging.info(
                f"{method.original.stratum.name}/{method.original.rdh.name}/"
                f"{method.original.name}"
            )

        # Compare each rdh to the nomod to get the not different snippets
        no_mod_snippets: list[Snippet] = []
        for method in methods:
            no_mod_snippets += method.compare_to_nomod(Path(self.input_dir))

        # Log information about the not different snippets
        self._store_snippets(no_mod_snippets, "no_mod_snippets.txt")
        logging.info(
            f"Strata: Number of not different snippets: {len(no_mod_snippets)}"
        )
        logging.info("Original method names of the not different snippets:")
        for snippet in no_mod_snippets:
            logging.info(f"{snippet.stratum.name}/{snippet.rdh.name}/{snippet.name}")

        # Shuffle the methods to make sure all stratas are equally represented
        random.shuffle(methods)

        # Create the surveys
        surveys = self.craft_sheets(methods)

        self._write_output(surveys)

    def craft_stratas(self) -> dict[str, Stratum]:
        """
        Craft the stratas from the input directory.
        :return: The stratas.
        """
        # Load the stratas and rdhs
        strata_names = self._load_stratas()
        self.num_stratas = len(strata_names)
        self.rdh_names = self._load_rdhs(strata_names)
        self.num_rdhs = len(self.rdh_names)

        # Create the int_to_key
        self._set_int_to_key(self.rdh_names)
        self._validate_configuration()

        # Convert the strats and rdhs to objects
        strata = {}
        for strata_name in strata_names:
            rdhs = {}
            for rdh_name in self.rdh_names:
                # Skip the nomod and original rdh
                if rdh_name == self.nomod_name or rdh_name == self.original_name:
                    continue

                # Add the rdh
                rdhs[rdh_name] = self._create_rdh(strata_name, rdh_name)

            # Add the original and nomod rdh
            original_rdh = self._create_rdh(strata_name, self.original_name)
            nomod_rdh = self._create_rdh(strata_name, self.nomod_name)

            # Create the methods from the rdhs, original and nomod
            methods = self._create_methods(rdhs, original_rdh, nomod_rdh)

            # Add the stratum
            strata[strata_name] = Stratum(strata_name, methods)

        return strata

    def _validate_configuration(self):
        # Check that the num_sheets and snippets_per_sheet are a multiple of num_rdhs
        if self.num_sheets % self.num_rdhs != 0:
            raise ValueError(
                "The number of sheets must be a multiple of the number of rdhs."
            )
        if self.snippets_per_sheet % self.num_rdhs != 0:
            raise ValueError(
                "The number of snippets per sheet must be a multiple of "
                "the number of rdhs."
            )

        # Check that the num_stratas length is equal to the sample_amount length
        if len(self.sample_amount) != self.num_stratas:
            raise ValueError("The sample amount must be specified for each stratum.")

        # Check that the sample amount summed up is <= num_rdhs * num_stratas
        if sum(self.sample_amount.values()) > self.num_rdhs * self.num_stratas:
            raise ValueError(
                "The sample amount summed up must be less than or equal "
                "to the number of rdhs times the number of stratas."
            )

    def _create_methods(
        self, rdhs: dict[str, RDH], original_rdh: RDH, nomod_rdh: RDH
    ) -> list[Method]:
        """
        Create the methods from the given rdhs, original and nomod.
        :param rdhs: The rdhs to create the methods from.
        :param original_rdh: The original rdh.
        :param nomod_rdh: The nomod rdh.
        :return: The methods.
        """
        methods = []
        for name, original_method in original_rdh.snippets.items():
            nomod_method = self._get_snippet(name, nomod_rdh)
            rdh_methods = {}
            for rdh in rdhs.values():
                rdh_methods[rdh.name] = self._get_snippet(name, rdh)
            methods.append(Method(original_method, nomod_method, rdh_methods))
        return methods

    @staticmethod
    def _get_snippet(name: str, rdh: RDH) -> Snippet:
        """
        Get the snippet with the given name from the given rdh. If the snippet does not
        exist, return a new NoSnippet.
        :param name: The name of the snippet.
        :param rdh: The rdh to get the snippet from.
        :return: The snippet.
        """
        snippet = rdh.get_snippet(name)
        if snippet is None:
            return NoSnippet(name, rdh)
        return snippet

    def _create_rdh(self, strata_name: str, rdh_name: str) -> RDH:
        """
        Create a rdh from the given rdh name and strata name.
        :param rdh_name: The name of the rdh.
        :param strata_name: The name of the strata.
        :return: The rdh.
        """
        snippet_names = list_non_hidden(
            os.path.join(self.input_dir, strata_name, rdh_name)
        )
        snippets = {
            snippet_name: Snippet(snippet_name) for snippet_name in snippet_names
        }
        return RDH(rdh_name, snippets)

    def _load_rdhs(self, strata_names: list[str]) -> list[str]:
        """
        Load the rdhs from the input directory.
        :param strata_names: The names of the stratas.
        :return: The rdh names and probabilities.
        """
        # Load the rdh names as the names of the subdirectories
        rdh_names = []
        for strata_name in strata_names:
            rdh_names += list_non_hidden(os.path.join(self.input_dir, strata_name))

        return list(set(rdh_names))

    def _load_stratas(self) -> list[str]:
        """
        Load the stratas from the input directory.
        :return: The strata names and probabilities.
        """
        # Load the strata names as the names of the subdirectories
        return list_non_hidden(self.input_dir)

    def _write_output(self, surveys: list[Survey]) -> None:
        """
        Write the output to the output directory.
        :param surveys: The surveys to write to the output directory.
        :return: The surveys.
        """
        # Create num_sheets output subdirectories
        for i in range(self.num_sheets):
            os.makedirs(os.path.join(self.output_dir, f"sheet_{i}"), exist_ok=True)

        # Copy the snippets to the output with name "idx_stratum_rdh_oldName"
        for i, survey in enumerate(surveys):
            random.shuffle(survey.snippets)
            for j, snippet in enumerate(survey.snippets):
                stratum = snippet.stratum.name
                rdh = snippet.rdh.name
                old_name = snippet.name
                new_name = f"{j}_{stratum}_{rdh}_{old_name}"
                if isinstance(snippet, NoSnippet):
                    logging.warning(
                        f"Survey {i}: Snippet {j}: "
                        f"{stratum}/{rdh}/{old_name} not found."
                    )

                    # Replace the first _ with / and remove everything after second _
                    source_path = old_name.replace("_", "/", 1).split("_")[0]
                    logging.info(f"None path:   none/none/{source_path}")
                    logging.info(f"Source path: {rdh}/{rdh}/{source_path}")
                    logging.info(
                        f"Goal path:   sheet_{i}/{j}_{stratum}_{rdh}_{old_name}"
                    )
                else:
                    shutil.copy(
                        os.path.join(self.input_dir, stratum, rdh, old_name),
                        os.path.join(self.output_dir, f"sheet_{i}", new_name),
                    )

    def craft_sheets(self, methods: list[Method]) -> list[Survey]:
        """
        Craft the surveys from the given strata. Each survey contains only one variant
        of each method.
        :param methods: The methods to sample from.
        :return: The sampled surveys.
        """
        permutations = permutation_matrix_3(
            sub_matrix_size=self.num_rdhs,
            width=self.snippets_per_sheet,
            height=self.num_sheets,
        )
        surveys = []
        for i in range(self.num_sheets):
            surveys.append(self._craft_sheet(methods, permutations[i]))

        return surveys

    def _craft_sheet(self, methods: list[Method], permutation: np.ndarray) -> Survey:
        """
        Craft a single sheet using the given methods and permutation array.
        :param methods: The methods to sample from.
        :param permutation: The permutation to use.
        :return: The sampled snippets.
        """
        snippets = []
        for i in range(self.snippets_per_sheet):
            method_idx, variant_idx = permutation[i]
            snippet = self._pick_snippet(methods, method_idx, variant_idx)
            snippets.append(snippet)

        return Survey(snippets)

    def sample_methods(
        self, strata: dict[str, Stratum], sample_amount: dict[str, int] = None
    ) -> list[Method]:
        """
        Sample methods from the given rdh name.
        :param strata: The strata to sample from.
        :param sample_amount: The amount of methods to sample per stratum.
        :return: The sampled methods.
        """
        # Initialize the sample amount
        sample_amount = sample_amount or self.sample_amount.copy()
        sampled = []

        # Iterate over the strata and sample the methods
        for stratum in strata.values():
            methods = stratum.methods
            sampled_methods = []
            for _i in range(sample_amount[stratum.name]):
                chosen = None
                while chosen is None or self._in_excluded(chosen):
                    chosen = methods.pop(random.randint(0, len(methods) - 1))
                sampled_methods.append(chosen)
            sampled += sampled_methods

        return sampled

    def _set_int_to_key(self, rdh_names: list[str]) -> None:
        """
        Calculate the int_to_key dict from the given rdh names and set it.
        :param rdh_names: The rdh names to use.
        :return: The int_to_key dict.
        """
        int_to_key = {}
        for i, rdh_name in enumerate(rdh_names):
            int_to_key[i] = rdh_name
        self.int_to_key = int_to_key

    def _pick_snippet(
        self, methods: list[Method], index: int, variant: str | int
    ) -> Snippet:
        """
        Obtain the variant of the method at the given index.
        :param methods: The methods to sample from.
        :param index: The index of the method.
        :param variant: The variant of the method.
        :return: The picked snippet.
        """
        if not isinstance(variant, str):
            variant = self.int_to_key[variant]
        return methods[index].pick_variant(variant)

    def _store_sampled_methods(
        self, methods: list[Method], filename: str = "chosen_methods.txt"
    ) -> None:
        """
        Store the originals of the sampled methods in a txt file in the output
        directory. The format is stratum/rdh/method.
        :param methods: The methods to store.
        :return: The stored methods.
        """
        with open(os.path.join(self.output_dir, filename), "w") as file:
            for method in methods:
                file.write(
                    f"{method.original.stratum.name}/"
                    f"{method.original.rdh.name}/"
                    f"{method.original.name}\n"
                )

    def _store_methods(self, methods: list[Method], filename: str) -> None:
        """
        Store the given methods in the given txt file in the output directory.
        The format is stratum/rdh/method.
        :param methods: The methods to store.
        :return: The stored methods.
        """
        with open(os.path.join(self.output_dir, filename), "w") as file:
            for method in methods:
                file.write(
                    f"{method.original.stratum.name}/"
                    f"{method.original.rdh.name}/"
                    f"{method.original.name}\n"
                )

    def _store_snippets(self, snippets: list[Snippet], filename: str) -> None:
        """
        Store the given snippets in the given txt file in the output directory.
        The format is stratum/rdh/method.
        :param snippets: The methods to store.
        :return: The stored methods.
        """
        with open(os.path.join(self.output_dir, filename), "w") as file:
            for snippet in snippets:
                file.write(
                    f"{snippet.stratum.name}/"
                    f"{snippet.rdh.name}/"
                    f"{snippet.name}\n"
                )

    def _in_excluded(self, chosen: Method) -> bool:
        """
        Check if the chosen method is in the excluded list. This is done by comparing
        the original method stratum/rdh/name with the excluded list.
        :param chosen: The chosen method.
        :return: True if the chosen method is in the excluded list, False otherwise.
        """
        in_excluded = (
            f"{chosen.original.stratum.name}/"
            f"{chosen.original.rdh.name}/"
            f"{chosen.original.name}" in self.exclude
        )
        if in_excluded:
            logging.info(
                f"Skipping excluded method: "
                f"{chosen.original.stratum.name}/"
                f"{chosen.original.rdh.name}/"
                f"{chosen.original.name}"
            )
        return in_excluded
