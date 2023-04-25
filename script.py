from models.mons import MonsConversion

import os
import re
import sys
import pandas as pd
import readline
import chardet
import uuid
import json

readline.set_completer_delims(' \t\n=')
readline.parse_and_bind("tab: complete")

# USER INPUT
# commenting out for development
# hbsmr_dir = ""
# while not (os.path.exists(hbsmr_dir) == True and os.path.isdir(hbsmr_dir) == True):
#     try:
#         hbsmr_dir = str(input("Specify path to HBSMR CSV export directory: "))
#     except NotADirectoryError:
#         print("Specified path is not a directory!")
#     except FileNotFoundError:
#         print("No directory found at specified path!")
hbsmr_dir = "../east_sussex/HBSMR-2020-CSV_Converted/"



#### ADD CHECK FOR IF ALL FILES ARE CORRECT ENCODING
# Currently add to dict to store encoding
encoding_dict = {}
for file in os.listdir(hbsmr_dir):
    filename = os.fsdecode(file)
    with open(hbsmr_dir+filename, 'rb') as rawdata:
        encoding_check = chardet.detect(rawdata.read(10000))
        if file not in encoding_dict.keys():
            encoding_dict[file] = encoding_check["encoding"]


### NEED TO HAVE IF .txt or .csv EXTENSION AND DO CONVERISONS





### Store all HBSMR UIDs and convert to Arches UUIDs
def add_uuid(input, d):
    if input not in d.keys():
        d[input] = str(uuid.uuid4())

uuid_conversion_dict = {}
# Only do if the json doesnt exist (so not created each time)
if not os.path.exists("hbsmr_to_arches_identifiers.json"):
    for file in os.listdir(hbsmr_dir):
        filename = os.fsdecode(file)
        try:
            if os.path.exists(hbsmr_dir+filename):
                try:
                    module_csv = pd.read_csv(hbsmr_dir+filename, na_filter=False)
                except UnicodeDecodeError:
                    module_csv = pd.read_csv(hbsmr_dir+filename, na_filter=False, encoding="latin-1", engine='python')

                cols_with_uid = [col for col in module_csv.columns if 'UID' in col]
                # Currently this just grabs all contents of any UID col which ends up with some numbers 
                for col in cols_with_uid:
                    for res_uid in module_csv[col]:
                        add_uuid(res_uid, uuid_conversion_dict)
        except FileNotFoundError:
            print("File not found")

    with open("hbsmr_to_arches_identifiers.json", "w") as outfile:
        json.dump(uuid_conversion_dict, outfile)

heritage_asset = MonsConversion.heritage_asset_conversion(hbsmr_dir, encoding_dict)
#maritime = MonsConversion.maritime_vessel_conversion(hbsmr_dir)
#test = MonsConversion.categorise_mons(hbsmr_dir)
