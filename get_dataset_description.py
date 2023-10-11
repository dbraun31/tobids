# taken from: https://github.com/bids-standard/bids-starter-kit/blob/main/pythonCode/createBIDS_dataset_description_json.py
# maybe the best way to do this is to code it as a function
# the function sources a script where each of these gets saved as a
# different var by a user
# then the function just puts it all in an ordered dict and returns
# function gets called in the pipeline

from collections import OrderedDict

def get_dataset_description():

    data = OrderedDict()
# General fields, shared with MRI BIDS and MEG BIDS:
# Required fields:
# name of the dataset
    data["Name"] = "Test data"

# The version of the BIDS standard that was used
    data["BIDSVersion"] = "1.0.2"

# Recommended fields:
# what license is this dataset distributed under?
# The use of license name abbreviations is suggested for specifying a license.
# A list of common licenses with suggested abbreviations can be found in appendix III.
    data["License"] = ""


# List of individuals who contributed to the creation/curation of the dataset
    data["Authors"] = ["", "", ""]

# who should be acknowledged in helping to collect the data
    data["Acknowledgements"] = ""

# Instructions how researchers using this dataset should acknowledge the original authors.
# This field can also be used to define a publication that should be cited in publications that use the dataset
    data["HowToAcknowledge"] = ""

# sources of funding (grant numbers)
    data["Funding"] = ["", "", ""]

# a list of references to publication that contain information on the dataset, or links.
    data["ReferencesAndLinks"] = ["", "", ""]

# the Document Object Identifier of the dataset (not the corresponding paper).
    data["DatasetDOI"] = ""

    return data


