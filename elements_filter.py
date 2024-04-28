from xml.etree import ElementTree as ET

# Load the XML file
file_path = '/mnt/data/lanelet2_map.osm'
tree = ET.parse(file_path)
root = tree.getroot()

# IDs of relations to keep
relation_ids_to_keep = {'109', '14', '108', '156', '155'}

# Collect IDs of ways and nodes to keep based on the relations
ways_to_keep = set()
nodes_to_keep = set()

# Find all relations and track the IDs of ways they reference
for relation in root.findall('relation'):
    if relation.get('id') in relation_ids_to_keep:
        for member in relation.findall('member'):
            if member.get('type') == 'way':
                ways_to_keep.add(member.get('ref'))

# Collect node IDs from the ways to be kept
for way in root.findall('way'):
    if way.get('id') in ways_to_keep:
        for nd in way.findall('nd'):
            nodes_to_keep.add(nd.get('ref'))

# Filter out unwanted relations, ways, and nodes
for relation in root.findall('relation'):
    if relation.get('id') not in relation_ids_to_keep:
        root.remove(relation)

for way in root.findall('way'):
    if way.get('id') not in ways_to_keep:
        root.remove(way)

for node in root.findall('node'):
    if node.get('id') not in nodes_to_keep:
        root.remove(node)

# Save the filtered XML to a new file
new_file_path = '/mnt/data/filtered_lanelet2_map.osm'
tree.write(new_file_path)
