import csv
import json
import os
from enum import Enum
from typing import Any

import requests
import yaml

API_URL = "https://api.github.com"
SEARCH = "search"
COMMITS = "commits"
CODE = "code"
REPOS = "repos"
RATE_LIMIT = "rate_limit"

CURR_DIR = os.path.dirname(os.path.relpath(__file__))
DATA_DIR = os.path.join(CURR_DIR, "../../../data")
RESOURCES_DIR = os.path.join(CURR_DIR, "../../res")

MAX_INT = 1000000

# No search for an exact string match here, but for filenames containing the following:
GITHUB_CHECKSTYLE_CONF_REG = (
    "extension:xml "
    "filename:checkstyle OR "
    "filename:check-style OR "
    "filename:sun OR "
    "filename:google"
)


def load(file_name: str, file_path: str = RESOURCES_DIR) -> dict:
    """
    Loads the given yaml file.
    :param file_name: The given file name.
    :param file_path: The given file path.
    :return: Returns the loaded yaml file as dict.
    """
    with open(os.path.join(file_path, file_name), encoding="utf-8") as file_stream:
        return yaml.safe_load(file_stream)


AUTH_TOKEN = load("credentials.yaml")["github_auth_token"]
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}


def get_unique_filename(dir_path, file_name):
    """
    Gets a new unique filename. Therefore, splits of the file extension if any,
    appends the index "_i" and adds the extension again until the filename is unique.
    :param dir_path: The directory to save the file in.
    :param file_name: The name of the file.
    :return: The new unique filename.
    """
    # Split the file extension if any
    file_name_split = file_name.split(".")
    file_name_without_extension = file_name_split[0]
    file_extension = ""
    if len(file_name_split) > 1:
        file_extension = "." + file_name_split[1]

    # Get a new unique filename
    i = 0
    while os.path.exists(os.path.join(dir_path, file_name)):
        i += 1
        file_name = file_name_without_extension + "_" + str(i) + file_extension

    return file_name


class DownloadFailedException(Exception):
    """
    Exception that is thrown whenever the download failed.
    """


class QueryMode(Enum):
    """
    Enum that defines the query mode for the code search.
    """

    # Search for repositories that contain "checkstyle" in their pom
    POM_WITH_CHECKSTYLE = 1

    # Search for repositories that have a checkstyle file
    CHECKSTYLE_FILE = 2


def _build_query(mode: QueryMode) -> str:
    """
    Builds the query for the code search.
    :param mode: The query mode for the code search.
    """
    if mode == QueryMode.POM_WITH_CHECKSTYLE:
        return "checkstyle filename:pom.xml"
    # elif mode == QueryMode.CHECKSTYLE_FILE:
    return GITHUB_CHECKSTYLE_CONF_REG


def _get_checkstyle_repos(
    per_page: int = 100,
    first_page: int = 1,
    last_page: int = 1,
    mode: QueryMode = QueryMode.CHECKSTYLE_FILE,
) -> tuple[dict[Any, Any], str | int] | tuple[Any, Any]:
    """
    Returns the repositories that contain a checkstyle plugin in their pom.xml.
    :param per_page: The amount of repositories per page.
    :param first_page: The first page to fetch.
    :param last_page: The last page to fetch.
    :param mode: The query mode for the code search.
    :return: Returns a tuple containing the repositories and the last downloaded page.
    """
    # Define the API endpoint and query parameters
    api_url = API_URL + "/" + SEARCH + "/" + CODE
    query_params = {
        "q": _build_query(mode),
        "per_page": per_page,
        "page": first_page,
    }

    data = {}

    while True:
        # Make the GET request
        response = requests.get(api_url, params=query_params, headers=HEADERS)

        # Check the response status code
        if response.status_code == 200:
            search_response_json = response.json()

            # Print the total amount of repositories on first request
            if query_params["page"] == 1:
                print(
                    f"Total amount of repositories: "
                    f"{search_response_json['total_count']}"
                )

            # Get each repo in the response
            for item in search_response_json["items"]:
                repository = item["repository"]
                repository_name = repository["full_name"]
                repository_url = repository["url"]

                # Open the repository url and save the json
                repository_response = requests.get(repository_url, headers=HEADERS)
                if repository_response.status_code == 200:
                    # Turn the json into a Munch object
                    # repository_response_json = munchify(repository_response.json())
                    repository_response_json = repository_response.json()
                    data[repository_name] = repository_response_json
                else:
                    # Request failed -> Return the current data and the last page
                    return data, query_params["page"]

            # Check if there are more pages to fetch
            if "next" in response.links and query_params["page"] < last_page:
                # Update the query parameters to fetch the next page
                query_params["page"] += 1
            else:
                # No more pages
                return data, query_params["page"]
        else:
            # Request failed -> Return the current data and the last page
            return data, query_params["page"]


def _remove_keys(
    data: dict[str, dict[str, str]], keys: list[str]
) -> dict[str, dict[str, str]]:
    """
    Removes the given keys from the given data.
    :param data: The given data.
    :param keys: The given keys.
    :return: Returns the data without the given keys.s
    """
    for key in keys:
        for item in data.values():
            item.pop(key, None)
    return data


class RepositorySortCriteria:
    """
    Class that represents the criteria to sort the repositories.
    The sort criteria is a list of tuples (key, weight).
    """

    def __init__(self, criteria=None) -> None:
        """
        Initializes the sort criteria.
        :param criteria: The sort criteria.
        """
        self.criteria = {}

        if criteria is not None and len(criteria) > 0:
            for key, value in criteria.items():
                weight = value["weight"]
                if "reverse" not in value:
                    self.add(key, weight)
                else:
                    reverse = value["reverse"]
                    self.add(key, weight, reverse)

    def add(self, key: str, weight: int, reverse: bool = False) -> None:
        """
        Adds a criterion to the sort criteria.
        :param key: The key to sort by.
        :param weight: The weight of the criterion.
        :param reverse: True if the criterion should be sorted in reverse order.
        """
        if reverse:
            weight *= -1
        self.criteria[key] = weight

    def custom_sort_key(self, item):
        """
        Returns the custom sort key for the given item.
        :param item: The given item.
        """
        return sum(
            self.criteria[key] * item[key] for key in item if key in self.criteria
        )

    @staticmethod
    def default():
        """
        Returns the default sort criteria.
        :return: The default sort criteria.
        """
        sorting_criteria = RepositorySortCriteria()
        sorting_criteria.add("forks_count", 1)
        sorting_criteria.add("stargazers_count", 1)
        return sorting_criteria


class RepositoryFilterCriteria:
    """
    Class that represents the criteria to filter the repositories.
    The filter criteria is a list of triples of:
    - (key, min, max) if the key is a number.
    - (key, value) if the key is a boolean.
    """

    def __init__(self, criteria=None) -> None:
        """
        Initializes the filter criteria.
        :param criteria: The filter criteria.
        """
        self.criteria = {}
        if criteria is not None and len(criteria) > 0:
            for key, value in criteria.items():
                if isinstance(value, dict):
                    if "min" not in value:
                        value["min"] = 0
                    if "max" not in value:
                        value["max"] = MAX_INT
                    self.add_range(key, value["min"], value["max"])
                else:
                    self.add_value(key, value)

    def add_value(self, key: str, expected: any) -> None:
        """
        Adds a value criterion to the filter criteria.
        :param key: The key to filter by.
        :param expected: The value of the criterion.
        """
        self.criteria[key] = expected

    def add_range(self, key: str, min_value: int = 0, max_value: int = MAX_INT) -> None:
        """
        Adds a min-max criterion to the filter criteria.
        :param key: The key to filter by.
        :param min_value: The minimum value of the criterion.
        :param max_value: The maximum value of the criterion.
        """
        self.criteria[key] = (min_value, max_value)

    def custom_filter_key(self, item):
        """
        Returns True if the item fulfills the filter criteria.
        :param item: The item to check.
        """
        for key, value in self.criteria.items():
            if (
                (isinstance(value, bool) and item[key] != value)
                or (isinstance(value, tuple) and not value[0] <= item[key] <= value[1])
                or (isinstance(value, str) and item[key] != value)
            ):
                return False
        return True

    @staticmethod
    def default():
        """
        Returns a default filter criteria.
        :return: The default filter criteria.
        """
        filter_criteria = RepositoryFilterCriteria()
        filter_criteria.add_value("private", False)
        filter_criteria.add_value("fork", False)
        filter_criteria.add_value("archived", False)
        filter_criteria.add_value("disabled", False)
        filter_criteria.add_value("language", "Java")
        filter_criteria.add_range("stargazers_count", 100, MAX_INT)
        filter_criteria.add_range("forks_count", 100, MAX_INT)
        filter_criteria.add_range("watchers_count", 100, MAX_INT)
        filter_criteria.add_range("open_issues_count", 0, MAX_INT)
        filter_criteria.add_range("subscribers_count", 10, MAX_INT)
        return filter_criteria


def download_repos(
    amount: int = 100,
    keys_to_keep: list = None,
    first_page: int = 1,
    mode: QueryMode = QueryMode.CHECKSTYLE_FILE,
) -> tuple[dict[str, dict[str, str]] | Any, Any]:
    """
    Returns repositories from GitHub that have a pom.xml file that contains a checkstyle
    plugin.
    :param amount: The amount of repositories to return.
    :param keys_to_keep: The keys to keep in the returned repositories.
    :param first_page: The first page to include in the returned repositories.
    :param mode: The mode to use to query the repositories.
    """
    per_page = 100
    if amount < 100:
        per_page = amount
    last_page = amount // per_page
    data, last_downloaded_page = _get_checkstyle_repos(
        per_page, first_page, last_page, mode
    )

    # Remove unnecessary keys if keys_to_keep is provided
    if keys_to_keep and len(keys_to_keep) > 0:
        all_keys = list(data.values())[0]
        keys_to_remove = [key for key in all_keys if key not in keys_to_keep]
        data = _remove_keys(data, keys_to_remove)

    return data, last_downloaded_page


def add_latest_commit(data: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    Adds the latest commit of the default branch to the repositories.
    :param data: The repositories to add the latest commit to.
    """
    try:
        for key, value in data.items():
            value["latest_commit"] = _get_latest_commit(key, value["default_branch"])
    except DownloadFailedException as e:
        print(e)
    return data


def filter_and_sort(
    data: dict[str, dict[str, str]],
    filter_criteria: RepositoryFilterCriteria = None,
    sorting_criteria: RepositorySortCriteria = None,
) -> dict[str, dict[str, str]]:
    """
    Filters out repositories based on the filter criteria and sorts them based on the
    sorting criteria.
    :param data: The repositories to filter and sort.
    :param filter_criteria: The filter criteria.
    :param sorting_criteria: The sorting criteria.
    """
    # Create equally weighted sorting criteria if it is not provided
    if sorting_criteria is None:
        sorting_criteria = RepositorySortCriteria.default()

    # Create filter criteria if it is not provided
    if filter_criteria is None:
        filter_criteria = RepositoryFilterCriteria.default()

    # Filter out repositories based on criteria
    data = {
        key: value
        for key, value in data.items()
        if filter_criteria.custom_filter_key(value)
    }

    # Sort the repositories
    sorted_dict = sorted(data.values(), key=sorting_criteria.custom_sort_key)
    return {item["full_name"]: item for item in sorted_dict}


def _get_latest_commit(full_name: str, default_branch: str) -> str:
    """
    Returns the latest commit of the default branch of the repository.
    :param full_name: The full name of the repository.
    :param default_branch: The default branch of the repository.
    """
    url = API_URL + "/" + REPOS + "/" + full_name + "/" + COMMITS + "/" + default_branch

    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        raise DownloadFailedException(
            f"Could not get the latest commit of the default branch of {full_name}."
        )
    return sha


def save_repos_as_json(
    data: dict[str, dict[str, str]],
    file_name: str,
    dir_path: str = DATA_DIR,
    overwrite_existing=False,
) -> None:
    """
    Saves the given repos as a json file.
    :param data: The data to save.
    :param file_name: The name of the file.
    :param dir_path: The directory to save the file in.s
    :param overwrite_existing: If True, the file will be overwritten if it exists.
    """
    if not overwrite_existing:
        file_name = get_unique_filename(dir_path, file_name)

    with open(os.path.join(dir_path, file_name), "w") as file:
        json.dump(data, file)


def load_repos_from_json(file_name: str, dir_path: str = DATA_DIR) -> dict[str, dict]:
    """
    Loads the repositories from the given json file.
    :param file_name: The name of the file.
    :param dir_path: The directory to load the file from.
    """
    with open(os.path.join(dir_path, file_name)) as file:
        return json.load(file)


def remove_empty_lines(file_name, dir_path):
    """
    Removes empty lines from the given file.
    :param file_name: The name of the file.
    :param dir_path: The directory of the file.
    """
    with open(os.path.join(dir_path, file_name), "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line.strip() != "":
                file.write(line)
        file.truncate()


def save_repos_as_csv(
    data: dict[str, dict[str, str]],
    file_name: str,
    dir_path: str = DATA_DIR,
    overwrite_existing=False,
) -> None:
    """
    Saves the given repos as a csv file.
    The csv file only contains the clone_url and the latest commit of the default
    branch.
    :param data: The data to save.
    :param file_name: The name of the file.
    :param dir_path: The directory to save the file in.
    :param overwrite_existing: If True, the file will be overwritten if it exists.
    """
    if not overwrite_existing:
        file_name = get_unique_filename(dir_path, file_name)

    with open(os.path.join(dir_path, file_name), "w") as file:
        writer = csv.writer(file)
        for repo in data.values():
            writer.writerow([repo["clone_url"], repo["latest_commit"]])

    remove_empty_lines(file_name, dir_path)


def get_remaining_requests():
    """
    Returns the amount of remaining requests.
    """
    response = requests.get(API_URL + "/" + RATE_LIMIT, headers=HEADERS)
    raw_data = response.json()
    used_data = {}

    if response.status_code == 200:
        for key, value in raw_data["resources"].items():
            if value["used"] != 0:
                used_data[key] = f"{value['used']} / {value['limit']}"
    else:
        return -1

    return used_data


def main():
    """
    Downloads checkstyle repositories and saves them as a json and csv file.
    """
    # Load the filter and sorting criteria
    download_criteria = load("download_criteria.yaml")
    filter_criteria = RepositoryFilterCriteria(download_criteria["filter_criteria"])
    sorting_criteria = RepositorySortCriteria(download_criteria["sorting_criteria"])

    # Get the repositories
    data, last_downloaded_page = download_repos(
        amount=1000000, mode=QueryMode.POM_WITH_CHECKSTYLE
    )
    print(f"Last downloaded page: {last_downloaded_page}")

    # Get the remaining requests
    remaining_requests = get_remaining_requests()
    if remaining_requests != -1:
        print(f"Used requests: {remaining_requests}")
    else:
        print("Could not get the remaining requests.")

    # Save the raw repositories
    save_repos_as_json(data, "repos_raw.json")
    print(f"Number of repositories: {len(data)}")

    # Add the latest commit to the repositories
    data = add_latest_commit(data)

    # Save the repositories with the latest commit
    save_repos_as_json(data, "repos_with_latest_commit.json")

    # Filter and sort the repositories
    data = filter_and_sort(data, filter_criteria, sorting_criteria)
    print(f"Number of repositories after filtering: {len(data)}")

    # Save the filtered repositories
    save_repos_as_json(data, "repos_filtered.json")
    save_repos_as_csv(data, "repos_filtered.csv")


if __name__ == "__main__":
    main()
