
#-------------------------------------------------------------------------------
# Icon and file path management for resources

def get_resource_icon_path(instance, filename):
    return get_attr_file_path(instance, filename, "icon", base_path="images")

