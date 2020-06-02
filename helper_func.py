
def formatDynamoResponse(entry):
    return_dict = {}
    for attrib_name, attrib_info in entry.items():
        for attrib_value in attrib_info.values():
            return_dict[attrib_name] = attrib_value
    
    return return_dict