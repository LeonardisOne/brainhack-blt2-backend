
def formatDynamoResponse(entry):
    return_dict = {}
    for attrib_name, attrib_info in entry.items():
        for attrib_value in attrib_info.values():
            return_dict[attrib_name] = attrib_value
    
    return return_dict

def getPostRequest(request, attrib_list):
    return_dict = {}
    for attrib_metadata in attrib_list:
        for attrib_name, attrib_type in attrib_metadata.items():
            return_dict[attrib_name] = { attrib_type: request.json.get(attrib_name) }
    
    return return_dict