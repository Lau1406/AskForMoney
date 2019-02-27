# Ask For Money
This program can make draft emails about who ows how much based on the data from a spreadsheet.
The `gmail_api.py` is based on the work of Chris Brown [GitHub Chris Brown](https://github.com/chris-brown-nz/python-gmail-api "gmail-api")

### Author
Made by L.J. Keijzer. Treasurer of E.S.Z.V. Boreas 2017-2018 [GitHub](https://github.com/Lau1406 "My GitHub")

## How To Use
Currently there is no self contained executable or run script that does all the work.
The current way to use it is by running
`python main.py --filename test_data.ods`
where 'test_data.ods' is the spreadsheet file that is in the same folder as main.py.
The first time the program is run it will open a browser window where it will ask you to authorise the program. 
Make sure you authorise the program with the same email address as is used in `client_secret.json` and the same as the `email` field in `config.ini`.

## Assumptions
For this program to work correctly, the following assumption were made:
* The sheet is called 'Debt'
* Every valid row has a length of at least 6
* The first 3 rows are not filled with actual data
* The first mention of an amount is in the 6th column (index 5) and the second mention is in the 12th column (index 11)
* The name of the person in in the 4th and 10th columns
* The decimal separator is a dot '.'
* All name entries of the same person are spelled the same, including the case of the letters
* The first column contains the names of the people and the second column the email address in the emails.csv file.
* Don't use commas ',' in the emails.csv file as part of the names of people

## Templating
The program supports some basic templating. 
This means that if certain keywords are used in a text, these will be replaced with other words. 
The following keywords can be used and what they will be replaced with:
```
<<D_NAME>>: The debtors name
<<C_NAME>>: The company or organization name
<<T_NAME>>: The senders name
<<AMOUNT>>: The amount of money owed for a single thing
<<T_AMOUNT>>: The total amount of money owed
<<ACCOUNT>>: The account number
<<REASONS>>: Multiple lines with the content of 'reason_row' from config.ini
<<REASON>>: The reason of a single thing
```
Usually `<<REASON>>` and `<<AMOUNT>>` are only used in a `reason_row` inside `<<REASONS>>`.

## Config Files
There are a couple of configuration files that can be changed to change the behaviour of the program.

#### config.ini
Inside this file some default values can be set. Below is the explanation of all values:
```ini
[main]
c_name = The name of the company or organization
t_name = The name of the person that sends the emails
account = The accout number
sheet_name = The title of the sheet in which the debtors are
email = The email from where the email are send

[template]
reason_row = The text of each row that explains for what is owed how much. Template tags are allowed here
subject = The email subject. Template tags are allowed here
```

#### client_secret.json
This is the file with the client secret in it. This can be downloaded from google from the gmail api. 
This only needs to be replaced if another account is used.

#### emails.csv
This is a comma separated values file which has the names of people in the first column and the associated email addresses in the second column.
These email addresses are used to fill in the destination email address. 
But if no email address can be found, no destination email address will be used.
Currently doesn't work with multiple email addresses for the same person.

#### message_content.txt
This file contains the template that will be used to write the content of the email. 
Templates can be used in this file.
