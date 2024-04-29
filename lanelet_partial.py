import lanelet2
from lanelet2.core import AttributeMap, GPSPoint, LaneletMap, Origin
from lanelet2.projection import UtmProjector
from lanelet2.io import load, write

# Load the full Lanelet2 map
full_map = load("path_to_full_map.osm", Origin(GPSPoint(latitude, longitude)))

# Define your area of interest (you can also use a bounding box or specific lanelet IDs)
area_of_interest = [...]  # List of lanelet IDs or GPS bounds

# Extract the submap
submap = LaneletMap()
for lanelet in full_map.laneletLayer:
    if lanelet.id in area_of_interest:
        submap.add(lanelet)

# Save the partial map
write("path_to_partial_map.osm", submap, AttributeMap())



import lanelet2
from lanelet2.core import AttributeMap, GPSPoint, LaneletMap, Origin
from lanelet2.projection import UtmProjector
from lanelet2.io import load, write

# Function to load map without regulatory elements
def load_map_without_regulatory_elements(path, origin):
    projector = UtmProjector(origin)
    # Load only the lanelet layer, ignoring regulatory elements
    lanelet_map = LaneletMap()
    with open(path, 'r') as file:
        lanelets_xml = lanelet2.io.load_lanlet_layer_from_xml(file, projector, lanelet_map)
    return lanelet_map

# Load the full Lanelet2 map, ignoring regulatory elements
latitude, longitude = 0, 0  # Replace with actual latitude and longitude
origin = Origin(GPSPoint(latitude, longitude))
full_map = load_map_without_regulatory_elements("path_to_full_map.osm", origin)

# Define your area of interest (you can also use a bounding box or specific lanelet IDs)
area_of_interest = [...]  # List of lanelet IDs or GPS bounds

# Extract the submap
submap = LaneletMap()
for lanelet in full_map.laneletLayer:
    if lanelet.id in area_of_interest:
        submap.add(lanelet)

# Save the partial map
write("path_to_partial_map.osm", submap, AttributeMap())


from xml.etree import ElementTree as ET

# Load the XML file
file_path = '/mnt/data/lanelet2_map.osm'
tree = ET.parse(file_path)
root = tree.getroot()

# List of subtype values for relation elements to remove
subtypes_to_remove = {'road_marking', 'no_stopping_area'}

# Track IDs of ways and nodes to remove
ways_to_remove = set()
nodes_to_remove = set()

# Collect relations that need to be removed based on subtype
relations_to_remove = []
for relation in root.findall('relation'):
    for tag in relation.findall('tag'):
        if tag.get('k') == 'subtype' and tag.get('v') in subtypes_to_remove:
            relations_to_remove.append(relation)
            # Collect way IDs from these relations
            for member in relation.findall('member'):
                if member.get('type') == 'way':
                    ways_to_remove.add(member.get('ref'))

# Collect node IDs from the ways to be removed
for way in root.findall('way'):
    if way.get('id') in ways_to_remove:
        for nd in way.findall('nd'):
            nodes_to_remove.add(nd.get('ref'))

# Remove the collected relations, ways, and nodes
for relation in relations_to_remove:
    root.remove(relation)

for way in root.findall('way'):
    if way.get('id') in ways_to_remove:
        root.remove(way)

for node in root.findall('node'):
    if node.get('id') in nodes_to_remove:
        root.remove(node)

# Save the modified XML to a new file
new_file_path = '/mnt/data/filtered_lanelet2_map.osm'
tree.write(new_file_path)

new_file_path


from xml.etree import ElementTree as ET

def remove_elements(xml_path, subtypes_to_remove):
    # Load the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # To keep track of all IDs to remove
    relations_to_remove = set()
    ways_to_remove = set()
    nodes_to_remove = set()

    # First pass: find all relations that need to be removed based on subtype
    for relation in root.findall('relation'):
        for tag in relation.findall('tag'):
            if tag.get('k') == 'subtype' and tag.get('v') in subtypes_to_remove:
                relations_to_remove.add(relation.get('id'))
                for member in relation.findall('member'):
                    if member.get('type') == 'way':
                        ways_to_remove.add(member.get('ref'))
                    elif member.get('type') == 'relation':
                        relations_to_remove.add(member.get('ref'))

    # Collect node IDs from the ways to be removed
    for way in root.findall('way'):
        if way.get('id') in ways_to_remove:
            for nd in way.findall('nd'):
                nodes_to_remove.add(nd.get('ref'))

    # Second pass: adjust for nested relations
    for relation in root.findall('relation'):
        for member in relation.findall('member'):
            if member.get('type') == 'relation' and member.get('ref') in relations_to_remove:
                relations_to_remove.add(relation.get('id'))

    # Removal process
    for relation in root.findall('relation'):
        if relation.get('id') in relations_to_remove:
            root.remove(relation)
    for way in root.findall('way'):
        if way.get('id') in ways_to_remove:
            root.remove(way)
    for node in root.findall('node'):
        if node.get('id') in nodes_to_remove:
            root.remove(node)

    # Save the modified XML to a new file
    new_file_path = xml_path.replace('.osm', '_filtered.osm')
    tree.write(new_file_path)
    return new_file_path

# Specify the path to your XML file and the subtypes to remove
xml_file_path = 'path_to_your_file.osm'  # Adjust to your file location
subtypes_list = ['road_marking', 'no_stopping_area']
new_file = remove_elements(xml_file_path, subtypes_list)

print("Filtered XML file saved as:", new_file)
