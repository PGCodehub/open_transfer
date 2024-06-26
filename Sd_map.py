import xml.etree.ElementTree as ET
import mgrs
import xml.dom.minidom

# Step 1: Parse the OSM File and Extract Node Coordinates and Way Information
osm_file_path = '/content/od_inter_map.osm'  # Replace with your OSM file path
tree = ET.parse(osm_file_path)
root = tree.getroot()

# Add parameter for filtering way IDs
way_ids_to_keep = ['59254388']  # Replace with your list of way IDs to keep

nodes = []
node_tags = {}
ways_info = {}

for node in root.findall('node'):
    node_id = node.get('id')
    lat = float(node.get('lat'))
    lon = float(node.get('lon'))
    tags = {tag.get('k'): tag.get('v') for tag in node.findall('tag')}
    
    # Remove tags if the node contains a highway key tag
    if 'highway' in tags:
        tags.pop('highway', None)
    
    nodes.append((node_id, lat, lon))
    node_tags[node_id] = tags

for way in root.findall('way'):
    way_id = way.get('id')
    way_nodes = [nd.get('ref') for nd in way.findall('nd')]
    way_tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
    
    # Filter for trunk, secondary, and tertiary highways
    if way_tags.get('highway') in ['trunk', 'secondary', 'tertiary']:
        # Retain only specific tags
        filtered_tags = {k: v for k, v in way_tags.items() if k in ['highway', 'oneway', 'lanes']}
        ways_info[way_id] = {
            'nodes': way_nodes,
            'tags': filtered_tags
        }

# Filter ways_info to keep only the specified way IDs
if way_ids_to_keep:
    ways_info = {way_id: info for way_id, info in ways_info.items() if way_id in way_ids_to_keep}

# Filter nodes to include only those referenced by the filtered ways
referenced_node_ids = {node_ref for way in ways_info.values() for node_ref in way['nodes']}
filtered_nodes = [(node_id, lat, lon) for node_id, lat, lon in nodes if node_id in referenced_node_ids]

print(f"Extracted {len(filtered_nodes)} nodes and {len(ways_info)} ways")

# Step 2: Calculate the Centroid of the Coordinates
def calculate_centroid(coords):
    if not coords:
        return None, None
    lat_sum = sum(lat for _, lat, _ in coords)
    lon_sum = sum(lon for _, _, lon in coords)
    centroid_lat = lat_sum / len(coords)
    centroid_lon = lon_sum / len(coords)
    return centroid_lat, centroid_lon

centroid_lat, centroid_lon = calculate_centroid(filtered_nodes)
print(f"Calculated centroid: Latitude={centroid_lat}, Longitude={centroid_lon}")

# Step 3: Convert the Centroid to the MGRS Grid
def latlon_to_mgrs(lat, lon, precision=5):
    m = mgrs.MGRS()
    mgrs_code = m.toMGRS(lat, lon, MGRSPrecision=precision)
    return mgrs_code

centroid_mgrs = latlon_to_mgrs(centroid_lat, centroid_lon, precision=3)
print(f"Centroid MGRS: {centroid_mgrs}")

# Step 4: Calculate MGRS Code for Each Node
local_nodes = {}
for node_id, lat, lon in filtered_nodes:
    mgrs_code = latlon_to_mgrs(lat, lon, precision=3)
    local_nodes[node_id] = (lat, lon, mgrs_code)

# Step 5: Write to a New XML File with Transformed Coordinates and Way Information
root = ET.Element("osm", version="0.6", generator="custom")

# Add the transformed nodes to the new XML structure
for node_id, (lat, lon, mgrs_code) in local_nodes.items():
    node = ET.SubElement(root, "node", id=str(node_id), visible='true', version='1', lat=str(lat), lon=str(lon))
    
    # Add additional tags
    # tags = node_tags.get(str(node_id), {})
    # for k, v in tags.items():
    #     ET.SubElement(node, "tag", k=k, v=v)
    
    # Add the MGRS code tag
    ET.SubElement(node, "tag", k='mgrs_code', v=mgrs_code)

# Add the ways to the new XML structure
for way_id, way_info in ways_info.items():
    way = ET.SubElement(root, "way", id=way_id, visible='true', version='1')
    
    # Add the node references
    for node_ref in way_info['nodes']:
        ET.SubElement(way, "nd", ref=node_ref)
    
    # Add only the specified tags
    for k, v in way_info['tags'].items():
        ET.SubElement(way, "tag", k=k, v=v)

# Convert the XML structure to a string and format it with proper spacing
xml_str = ET.tostring(root, encoding='unicode')
xml_str = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")

# Write the formatted XML to a file
output_file_path = '/content/filtered_center_map.osm'
with open(output_file_path, 'w', encoding='utf-8') as f:
    f.write(xml_str)

print(f"Transformed map written to {output_file_path}")


import osmium as osm
import math
import xml.etree.ElementTree as ET
from xml.dom import minidom
import mgrs

class LaneletHandler(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.nodes = {}
        self.node_tags = {}
        self.ways = {}
        self.way_tags = {}

    def node(self, n):
        self.nodes[n.id] = (n.location.lat, n.location.lon)
        self.node_tags[n.id] = {tag.k: tag.v for tag in n.tags}

    def way(self, w):
        self.ways[w.id] = [n.ref for n in w.nodes]
        self.way_tags[w.id] = {tag.k: tag.v for tag in w.tags}

handler = LaneletHandler()
handler.apply_file('filtered_center_map.osm')

nodes = handler.nodes
node_tags = handler.node_tags
ways = handler.ways
way_tags = handler.way_tags

# Function to calculate the offset points to the left and right of a given point
def calculate_offsets(lat, lon, distance, angle):
    R = 6378137  # Radius of Earth in meters
    dn = distance * math.sin(angle)
    de = distance * math.cos(angle)
    
    dLat = dn / R
    dLon = de / (R * math.cos(math.pi * lat / 180))
    
    lat_offset = lat + dLat * 180 / math.pi
    lon_offset = lon + dLon * 180 / math.pi
    
    return lat_offset, lon_offset

# Function to convert latitude and longitude to MGRS
def latlon_to_mgrs(lat, lon, precision=3):
    m = mgrs.MGRS()
    mgrs_code = m.toMGRS(lat, lon, MGRSPrecision=precision)
    return mgrs_code

average_width = 6.223256958160823 / 2  # Half width for each side

# Section to create left and right ways for each way using the calculate_offsets function and average_width
way_offsets = {}

for way_id, node_ids in ways.items():
    left_way = []
    right_way = []

    for node_id in node_ids:
        lat, lon = nodes[node_id]
        left_lat, left_lon = calculate_offsets(lat, lon, average_width, math.pi / 2)  # 90 degrees for left
        right_lat, right_lon = calculate_offsets(lat, lon, average_width, -math.pi / 2)  # -90 degrees for right
        
        left_way.append((left_lat, left_lon))
        right_way.append((right_lat, right_lon))
    
    way_offsets[way_id] = {
        'left': left_way,
        'right': right_way
    }

# Function to identify related ways
def identify_related_ways(ways):
    related_ways = {}

    # Convert ways to sets of node references for easier comparison
    way_node_sets = {way_id: set(node_refs) for way_id, node_refs in ways.items()}

    # Compare each pair of ways to find related ones
    for way_id_1, node_set_1 in way_node_sets.items():
        related_ways[way_id_1] = []
        for way_id_2, node_set_2 in way_node_sets.items():
            if way_id_1 != way_id_2 and node_set_1 & node_set_2:
                related_ways[way_id_1].append(way_id_2)

    return related_ways

related_ways = identify_related_ways(ways)

# Function to create a mapping for related left ways
def map_related_left_ways(related_ways, way_offsets):
    related_left_ways = {}

    for way_id, related_way_ids in related_ways.items():
        related_left_ways[way_id] = {
            'left': way_offsets[way_id]['left'],
            'related_left': []
        }
        for related_way_id in related_way_ids:
            related_left_ways[way_id]['related_left'].append(way_offsets[related_way_id]['left'])

    return related_left_ways

related_left_ways = map_related_left_ways(related_ways, way_offsets)

# Function to create a mapping for related right ways
def map_related_right_ways(related_ways, way_offsets):
    related_right_ways = {}

    for way_id, related_way_ids in related_ways.items():
        related_right_ways[way_id] = {
            'right': way_offsets[way_id]['right'],
            'related_right': []
        }
        for related_way_id in related_way_ids:
            related_right_ways[way_id]['related_right'].append(way_offsets[related_way_id]['right'])

    return related_right_ways

related_right_ways = map_related_right_ways(related_ways, way_offsets)

# Function to add nodes, ways, and relations to the XML
def add_ways_to_xml(related_ways, way_offsets, side, global_id_counter, way_type):
    node_id_map = {}  # Map to keep track of new node IDs
    way_id_map = {}  # Map to keep track of new way IDs for relations

    for way_id, way_data in related_ways.items():
        way_nodes = way_data[side]
        related_ways_nodes = way_data[f'related_{side}']

        way_elem = ET.SubElement(root, "way", id=str(global_id_counter), visible='true', version='1')
        way_id_map[way_id] = global_id_counter
        global_id_counter += 1

        # Add way tags
        ET.SubElement(way_elem, "tag", k='subtype', v='solid')
        ET.SubElement(way_elem, "tag", k='type', v='line_thin')
        ET.SubElement(way_elem, "tag", k='width', v='0.200')

        # Add nodes for the way
        for lat, lon in way_nodes:
            node_id = node_id_map.get((lat, lon))
            if node_id is None:
                node_id = global_id_counter
                global_id_counter += 1
                node_id_map[(lat, lon)] = node_id
                node_elem = ET.SubElement(root, "node", id=str(node_id), lat=str(lat), lon=str(lon), visible='true', version='1')
                ET.SubElement(node_elem, "tag", k='ele', v='0')  # Default ele value
                mgrs_code = latlon_to_mgrs(lat, lon)
                ET.SubElement(node_elem, "tag", k='mgrs_code', v=mgrs_code)
            ET.SubElement(way_elem, "nd", ref=str(node_id))

        # Ensure related ways share common node references
        for related_nodes in related_ways_nodes:
            common_nodes = set(way_nodes) & set(related_nodes)

            for lat, lon in common_nodes:
                node_id = node_id_map.get((lat, lon))
                if node_id is None:
                    node_id = global_id_counter
                    global_id_counter += 1
                    node_id_map[(lat, lon)] = node_id
                    node_elem = ET.SubElement(root, "node", id=str(node_id), lat=str(lat), lon=str(lon), visible='true', version='1')
                    ET.SubElement(node_elem, "tag", k='ele', v='0')  # Default ele value
                    mgrs_code = latlon_to_mgrs(lat, lon)
                    ET.SubElement(node_elem, "tag", k='mgrs_code', v=mgrs_code)
                ET.SubElement(way_elem, "nd", ref=str(node_id))

            related_way_elem = ET.SubElement(root, "way", id=str(global_id_counter), visible='true', version='1')
            global_id_counter += 1
            ET.SubElement(related_way_elem, "tag", k='subtype', v='solid')
            ET.SubElement(related_way_elem, "tag", k='type', v='line_thin')
            ET.SubElement(related_way_elem, "tag", k='width', v='0.200')
            for lat, lon in related_nodes:
                node_id = node_id_map.get((lat, lon))
                if node_id is None:
                    node_id = global_id_counter
                    global_id_counter += 1
                    node_id_map[(lat, lon)] = node_id
                    node_elem = ET.SubElement(root, "node", id=str(node_id), lat=str(lat), lon=str(lon), visible='true', version='1')
                    ET.SubElement(node_elem, "tag", k='ele', v='0')  # Default ele value
                    mgrs_code = latlon_to_mgrs(lat, lon)
                    ET.SubElement(node_elem, "tag", k='mgrs_code', v=mgrs_code)
                ET.SubElement(related_way_elem, "nd", ref=str(node_id))

    return global_id_counter, way_id_map

# Initialize the new XML structure
root = ET.Element("osm", version="0.6")
global_id_counter = 1000000  # Global ID counter starting from a high number to avoid conflicts

# Add left ways and nodes to the new XML
global_id_counter, left_way_id_map = add_ways_to_xml(related_left_ways, way_offsets, 'left', global_id_counter, 'left')

# Add right ways and nodes to the new XML
global_id_counter, right_way_id_map = add_ways_to_xml(related_right_ways, way_offsets, 'right', global_id_counter, 'right')

# Function to add relations to the XML
def add_relations_to_xml(left_way_id_map, right_way_id_map, global_id_counter):
    relation_id_counter = global_id_counter

    for way_id in left_way_id_map.keys():
        relation_elem = ET.SubElement(root, "relation", id=str(relation_id_counter), visible='true', version='1')
        relation_id_counter += 1

        ET.SubElement(relation_elem, "member", type='way', ref=str(left_way_id_map[way_id]), role='left')
        ET.SubElement(relation_elem, "member", type='way', ref=str(right_way_id_map[way_id]), role='right')

        ET.SubElement(relation_elem, "tag", k='location', v='urban')
        # ET.SubElement(relation_elem, "tag", k='one_way', v='yes')
        ET.SubElement(relation_elem, "tag", k='speed_limit', v='10')
        ET.SubElement(relation_elem, "tag", k='subtype', v='road')
        ET.SubElement(relation_elem, "tag", k='type', v='lanelet')

    return relation_id_counter

# Add relations to the XML
global_id_counter = add_relations_to_xml(left_way_id_map, right_way_id_map, global_id_counter)

# Pretty print and save the XML as a .osm file
tree = ET.ElementTree(root)
xml_str = ET.tostring(root, encoding='utf-8')
xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
with open("new_map.osm", "w") as f:
    f.write(xml_pretty_str)

print("New .osm file with left and right ways, nodes, and relations has been created as 'new_map.osm'.")
