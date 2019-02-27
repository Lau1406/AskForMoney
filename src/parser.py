import constants
from configparser import ConfigParser
from decimal import Decimal


class Parser:
    # Variables
    two_places = Decimal(10) ** -2
    config = ConfigParser()
    config.read(constants.config_file)

    def __init__(self):
        """
        constructor that reads the data from the supplied files. If these files cannot be found, it creates them
        """
        # TODO: add check to see if the config.ini file is present, if not create it
        # Get all data from the config file
        # All the already defined data
        self.c_name = self.config.get("main", "c_name")
        self.t_name = self.config.get("main", "t_name")
        self.account = self.config.get("main", "account")
        self.reason_row = self.config.get("template", "reason_row")

        # The template text
        f = open(constants.template_file)
        self.template = f.read()

    def parse(self, name: str, debits: list, template: str) -> str:
        """
        Function that can parse a template text based on the imported template tags and the data needed for a debtor.
        :param name: the name of the debtor
        :param debits: a list of dictionaries containing the data for every debit in the form of
        {
            "amount": the amount,
            "reason": the reason
        }
        :param template: the template to use, if empty, uses the default template
        :return: the parsed message
        """

        if template == "":
            template = self.template

        total = 0
        reasons = ""
        for d in debits:
            total += d["amount"]
            reasons += self.reason_row \
                           .replace(constants.tag_reason, d["reason"]) \
                           .replace(constants.tag_amount, str(Decimal(d["amount"]).quantize(self.two_places))) + "\n"

        # Replace all tags in message with data
        message = template\
            .replace(constants.tag_d_name, name)\
            .replace(constants.tag_c_name, self.c_name)\
            .replace(constants.tag_t_name, self.t_name)\
            .replace(constants.tag_total_amount, str(Decimal(total).quantize(self.two_places)))\
            .replace(constants.tag_account, self.account)\
            .replace(constants.tag_reasons, reasons)

        return message
