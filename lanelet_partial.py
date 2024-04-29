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
