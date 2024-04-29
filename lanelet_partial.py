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
