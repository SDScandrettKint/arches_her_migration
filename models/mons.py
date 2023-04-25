import pandas as pd
import json
import os
import sys
import logging
import re
from models.geometries import GeometryConversion

logging.basicConfig(filename='Migration_HeritageAsset.log', filemode='a+', format='%(asctime)s - %(message)s', level=logging.DEBUG)

class MonsConversion():

    def generate_start_csv():
        df = pd.DataFrame(columns=['ResourceID'])
        return df


    def open_file(p, tablename):
        try:
            try:
                return_csv = pd.read_csv("%s%s.csv" % (p, tablename), na_filter=False)
                return return_csv
            except UnicodeDecodeError:
                return_csv = pd.read_csv("%s%s.csv" % (p, tablename), na_filter=False, encoding="latin-1", engine='python')  
                return return_csv
        except FileNotFoundError:
            print("File not found at location %s%s.csv" % (p, tablename))
            sys.exit(1)


    def categorise_mons(dir_path):
        try:  
            try:
                mon_csv = pd.read_csv(dir_path+"Table_Mon.csv", na_filter=False)
            except UnicodeDecodeError:
                mon_csv = pd.read_csv(dir_path+"Table_Mon.csv", na_filter=False, encoding="latin-1", engine='python')  

            heritage_assets = []
            heritage_areas = []
            maritime_vessels = []
            historic_aircrafts = []
            for uid, recordtype in (zip(mon_csv['MonUID'], mon_csv['RecordType'])):
                if recordtype in ('MON','BLD','HED'):
                    heritage_assets.append(uid)
                elif recordtype in ('FS', 'LND', 'PLA'):
                    heritage_areas.append(uid)
                elif recordtype == "MAR":
                    maritime_vessels.append(uid)

            return (heritage_assets, heritage_areas, maritime_vessels, historic_aircrafts)

        except FileNotFoundError:
            print("File not found at %sTable_Mon.csv" % (dir_path))
            sys.exit(1)


    def heritage_asset_conversion(dir_path, encodings):
        #Open CSVs
        mon_csv = MonsConversion.open_file(dir_path, "Table_Mon")
        topology_lut = MonsConversion.open_file(dir_path, "Table_GeoTopologyLUT")

        # Open mappings & store
        with open("hbsmr_to_arches_identifiers.json") as f:
            mapping_dict = json.loads(f.read())
        with open("arches_mapping_files/Heritage Asset_concepts.json") as f:
            heritage_asset_concept_json = json.loads(f.read())

        heritage_assets_list = MonsConversion.categorise_mons(dir_path)[0]
        print(len(heritage_assets_list))
        heritage_asset_csv = MonsConversion.generate_start_csv()
        heritage_asset_csv["Legacy ID"] = ""





        # Adding resourceID and legacy id to csv
        # asset_mon_mappings = {}
        # for hbsmr_monuid in mon_csv["MonUID"]:
        #     if hbsmr_monuid in heritage_assets_list:
        #         arches_uuid = mapping_dict[hbsmr_monuid]

        #         if arches_uuid not in asset_mon_mappings.keys():
        #             asset_mon_mappings[arches_uuid] = hbsmr_monuid

        # heritage_asset_csv["ResourceID"] = asset_mon_mappings.keys()
        # heritage_asset_csv["Legacy ID"] = asset_mon_mappings.values() 

        

        asset_mon_mappings = {}
        index = 0
        for (hbsmr_monuid,name,summary,desc,topology,point,line,polygon) in zip(mon_csv["MonUID"],
                                                              mon_csv["Name"],
                                                              mon_csv["Summary"],
                                                              mon_csv["Descr"],
                                                              mon_csv["Topology"],
                                                              mon_csv["WKTPoint"],
                                                              mon_csv["WKTLine"],
                                                              mon_csv["WKTPolygon"]):
            # if the monument is a heritage asset -
            if hbsmr_monuid in heritage_assets_list:
                arches_uuid = mapping_dict[hbsmr_monuid]
                
                ## Format Summary/Description rich text
                full_desc = "<p>Summary:<p/><p>%s</p><br><p>Description:</p>" % (summary) #concat summary and desc
                # Use encodings to find if newline encoded by \r\n or \n
                try:
                    if re.search("Windows", encodings["Table_Mon.csv"], re.IGNORECASE):
                        # summary can have new lines but from looks of things shouldnt at times so make into one line
                        if "\r\n" in summary:
                            list_of_summary_lines = summary.split("\r\n")
                            for summaryindex, each in enumerate(list_of_summary_lines):
                                list_of_summary_lines[summaryindex] = each.strip()
                            full_summ = ' '.join(list_of_summary_lines)
                            full_desc = "<p>Summary:<p/><p>%s</p><br><p>Description:</p>" % (full_summ) 
                        elif "\n" in summary:
                            list_of_summary_lines = summary.split("\n")
                            for summaryindex, each in enumerate(list_of_summary_lines):
                                list_of_summary_lines[summaryindex] = each.strip()
                            full_summ = ' '.join(list_of_summary_lines)
                            full_desc = "<p>Summary:<p/><p>%s</p><br><p>Description:</p>" % (full_summ)
                        else:
                            full_desc = "<p>Summary:<p/><p>%s</p><br><p>Description:</p>" % (summary)

                        # Description should be split on new lines 
                        if "\r\n" in desc:
                            list_of_desc_lines = desc.split("\r\n")
                            for each in list_of_desc_lines:
                                full_desc += "<p>%s</p>" % (each)
                        elif "\n" in desc:
                            list_of_desc_lines = desc.split("\n")
                            for each in list_of_desc_lines:
                                full_desc += "<p>%s</p>" % (each)
    
                    else: # if encoding not windows (so just \n)
                        if "\n" in summary:
                            list_of_summary_lines = summary.split("\n")
                            for summaryindex, each in enumerate(list_of_summary_lines):
                                list_of_summary_lines[summaryindex] = each.strip()
                            full_summ = ' '.join(list_of_summary_lines)
                            full_desc = "<p>Summary:<p/><p>%s</p><br><p>Description:</p>" % (full_summ)
                        else:
                            full_desc = "<p>Summary:<p/><p>%s</p><br><p>Description:</p>" % (summary)

                        if "\n" in desc:
                            list_of_desc_lines = desc.split("\n")
                            for each in list_of_desc_lines:
                                full_desc += "<p>%s</p>" % (each)
                            
                except KeyError:
                    print("Table Mon.csv does not exist in encodings dictionary")

                
                # Add quotes around desc in case there are commas/semi colons in text
                full_desc = "\"%s\"" % (full_desc)

                if topology in topology_lut["Topology"].values:
                    topology_index = topology_lut[topology_lut["Topology"] == topology].index.tolist()
                    topology_desc = topology_lut.loc[topology_index, "Desc"].values[0] #now point instead of P
                
                # Because the LUT doesnt change, mapping should work all the time with similar words 
                for k,v in heritage_asset_concept_json["Shape Qualifier"].items():
                    if topology_desc in v:
                        topology_value_uuid = k
                    else: # the ones with different wordings
                        if topology_desc == "Radial":
                            print("Unmapped concept! Topology - %s" % (topology_desc))
                            logging.warning("Unmapped concept! Topology - %s" % (topology_desc))


                # Geometry
                print("RESOURCE",point, line, polygon)
                GeometryConversion.do_geom_conversion(point,line,polygon)
                #GeometryConversion.point_geom(point)
                breakpoint()



                # Map to nested dict
                asset_mon_mappings[index] = {"ResourceID":arches_uuid,
                                             "Legacy ID":hbsmr_monuid,
                                             "Asset Name":name,
                                             "Description":full_desc,
                                             "Feature Shape":topology_value_uuid}
                index+=1

        heritage_asset_csv = pd.DataFrame.from_dict(asset_mon_mappings,orient='index')
        heritage_asset_csv.to_csv("Heritage_Assets.csv", index=False)



    def maritime_vessel_conversion(dir_path):
        maritime_resources = MonsConversion.categorise_mons(dir_path)[2]
        print(len(maritime_resources))

        try:
            if os.path.exists(dir_path+"Table_MonMaritime.csv"):
                try:
                    mon_maritime_csv = pd.read_csv(dir_path+"Table_MonMaritime.csv", na_filter=False)
                except UnicodeDecodeError:
                    mon_maritime_csv = pd.read_csv(dir_path+"Table_MonMaritime.csv", na_filter=False, encoding="latin-1", engine='python')  
        except FileNotFoundError:
            print("File not found")

        # try:
        #     if os.path.exists(dir_path+"Table_Mon.csv"):
        #         try:
        #             mon_csv = pd.read_csv(dir_path+"Table_Mon.csv", na_filter=False)
        #         except UnicodeDecodeError:
        #             mon_csv = pd.read_csv(dir_path+"Table_Mon.csv", na_filter=False, encoding="latin-1", engine='python')  


        # Create new df for Arches Maritime Vessel model
        m_vessel_csv = mon_maritime_csv[['MonUID']]

        # vessel
        # vessel_lut =  pd.read_csv(dir_path + "Table_TermLUT.csv", na_filter=False, encoding="latin-1", engine='python')
        # for num, col in enumerate(mon_maritime_csv['VesselType']):
        #     if col != "0":
        #         vessel_lut[vessel_lut[''].str.contains("hello")]
        #         # termID and term
                

