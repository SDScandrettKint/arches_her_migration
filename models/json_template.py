import json

def starting_template():

    json_start_str = """{"business_data": {"resources": []}}"""
    json_start_json = json.loads(json_start_str)
    return json_start_json

def new_resource(graph_UUID, legacy_ID, res_UUID):

    newres_str = ((
"""{
    "resourceinstance": {
        "descriptors": None,
        "graph_id": "%s",
        "legacyid": "%s",
        "name": "None",
        "resourceinstanceid": "%s"
    },
    "tiles": [
        ]
    }
     """) % (graph_UUID, legacy_ID, res_UUID))
    newres_json = json.loads(newres_str)
    return newres_json