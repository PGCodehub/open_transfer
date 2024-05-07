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



import argparse
from xml.etree import ElementTree as ET

def filter_xml_elements(xml_path, relation_ids_to_keep):
    """
    Filters an XML file to keep only specified relation elements and their associated ways and nodes.

    Args:
        xml_path (str): The path to the XML file to filter.
        relation_ids_to_keep (list of int): A list of relation IDs that should be preserved in the XML.

    Returns:
        str: The path to the new, filtered XML file.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Convert list to a set for faster operations
    relation_ids_to_keep = set(map(str, relation_ids_to_keep))

    # To keep track of all IDs to preserve
    ways_to_keep = set()
    nodes_to_keep = set()
    additional_relations_to_keep = set()

    # First pass: Collect all relations, ways, and nodes from the specified relations
    for relation in root.findall('relation'):
        if relation.get('id') in relation_ids_to_keep:
            for member in relation.findall('member'):
                if member.get('type') == 'way':
                    ways_to_keep.add(member.get('ref'))
                elif member.get('type') == 'node':
                    nodes_to_keep.add(member.get('ref'))
                elif member.get('type') == 'relation':
                    additional_relations_to_keep.add(member.get('ref'))

    # Add referenced relations to the set of relations to keep
    relation_ids_to_keep.update(additional_relations_to_keep)

    # Collect node IDs from the ways to be kept
    for way in root.findall('way'):
        if way.get('id') in ways_to_keep:
            for nd in way.findall('nd'):
                nodes_to_keep.add(nd.get('ref'))

    # Second pass: Remove all elements that are not to be kept
    root[:] = [element for element in root if (
        (element.tag == 'relation' and element.get('id') in relation_ids_to_keep) or
        (element.tag == 'way' and element.get('id') in ways_to_keep) or
        (element.tag == 'node' and element.get('id') in nodes_to_keep)
    )]

    # Save the modified XML to a new file
    new_file_path = xml_path.replace('.osm', '_filtered.osm')
    tree.write(new_file_path)
    return new_file_path

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Filter XML file to keep specific relations and their dependencies.")
    parser.add_argument("xml_file", type=str, help="Path to the XML file to be processed.")
    parser.add_argument("relation_ids", type=int, nargs='+', help="List of relation IDs to keep.")
    args = parser.parse_args()

    # Filter the XML file based on the provided IDs
    filtered_file = filter_xml_elements(args.xml_file, args.relation_ids)


Add filter_xml_elements to selectively retain relations and dependencies in XML files
- Allows filtering based on relation IDs via command-line arguments
- Preserves related ways and nodes to maintain integrity of the XML structure

    print("Filtered XML file saved as:", filtered_file)

if __name__ == "__main__":
    main()
