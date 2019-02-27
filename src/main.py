import re
import constants
from parser import Parser
from pyexcel_ods3 import get_data
from configparser import ConfigParser
import csv
import gmail_api


# TODO: read from memory
# TODO: add unittests
# TODO: make standalone executable
# https://stackoverflow.com/questions/5458048/how-to-make-a-python-script-standalone-executable-to-run-without-any-dependency#5458807
# TODO: add name to email map
# TODO: check if config file is correct
# TODO: make more robust
"""

:author L.J. Keijzer, Treasurer E.S.Z.V. Boreas 2017-2018
"""


def parse_amount(amount) -> float:
    """
    Function to convert a string with a float in it to a float
    :param amount: the input string
    :return: the float in the string
    """
    if type(amount) is int:
        return float(amount)
    elif type(amount) is str:
        try:
            ans = float(re.search(r'[+-]?([0-9]*[.])?[0-9]+', amount).group())
        except:
            return 0
        return ans
    elif type(amount) is float:
        return amount
    else:
        return 0


def extract_data(row: list) -> dict:
    """
    Function that extracts all useful data from a row
    :param row: the row
    :return: a dictionary with all the relevant data
    """
    if len(row) < 6:
        return {
            "error": True
        }

    # Get all relevant data
    data = {
        "error": False,
        "name": row[3],
        "reason": row[4],
        "owed": round(parse_amount(row[5]), 2) if len(row) < 12
        else round(parse_amount(row[5]), 2) - round(parse_amount(row[11]), 2)
    }

    return data


def get_email_addresses() -> dict:
    """
    Function that reads the emails.csv file and returns a dictionary that can server as a one way mapping based on the data from the file.
    The first column is the name of the person and the second column the email address.
    Leading and trailing spaces are removed
    :return: the dictionary with the mapping
    """
    mapping = {}
    with open("emails.csv", mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in reader:
            if len(row) < 2:
                continue
            mapping[row[0].lower().strip()] = row[1].strip()

    return mapping


def create_argument_parser():
    """
    Function that returns an argumet parser with some extra arguments added
    :return: the parser
    """
    try:
        import argparse
    except ImportError:  # pragma: NO COVER
        return None
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--filename",
                        help="The file to read.")
    return parser


def main() -> None:
    """
    The main method that is in control of getting it all done
    :return: None
    """

    # Not sure why this is needed twice, but it doesn't work otherwise. Also needed in gmail_api.py
    argparser = create_argument_parser()
    args = argparser.parse_args()

    config = ConfigParser()
    config.read(constants.config_file)

    api = gmail_api.PythonGmailAPI()

    parser = Parser()

    # Get all data
    data = get_data(args.filename)[config.get("main", "sheet_name")]
    # data = get_data(file_name)[config.get("main", "sheet_name")]

    subject_template = config.get("template", "subject")
    my_email = config.get("main", "email")

    # Read email addresses that are linked to names
    email_mapping = get_email_addresses()

    # To store the debtors in
    debits = {}
    # To store all the messages in
    messages = {}

    # Loop over all rows
    for i in range(len(data)):
        row = data[i]
        if i < 3 or len(row) < 6 or not row[0]:
            # Skip the first 3 lines and if the amount of columns is less than 6 and if the first column is empty
            continue

        results = extract_data(row)

        # Skip if there is nothing owed in this row
        if results["owed"] <= 0 or results["error"]:
            continue

        # Store data
        if results["name"] in debits:
            debits[results["name"]].append({
                "reason": results["reason"],
                "amount": results["owed"]
            })
        else:
            debits[results["name"]] = [{
                "reason": results["reason"],
                "amount": results["owed"]
            }]

    # Go over all debtors and generate the text
    for name in debits:
        print("Processing %s" % name)
        debt = 0
        for d in debits[name]:
            debt += d["amount"]

        messages[name] = parser.parse(name, debits[name], "")

        # Create draft
        subject = parser.parse(name, debits[name], subject_template)
        to = email_mapping[name.lower()] if name.lower() in email_mapping else ""
        # Actually create the draft on gmail
        api.gmail_draft(my_email, to, subject, messages[name])


if __name__ == "__main__":
    main()
