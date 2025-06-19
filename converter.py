import json
import argparse

def convert_to_aperio_geojson(input_filename, output_filename):
    """
    Converts a specific JSON annotation format to a GeoJSON format
    compatible with Aperio.

    Args:
        input_filename (str): The path to the input JSON annotation file.
        output_filename (str): The path where the output GeoJSON file will be saved.
    """
    try:
        with open(input_filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{input_filename}'.")
        return

    # Initialize the structure for a GeoJSON FeatureCollection
    geojson_output = {
        "type": "FeatureCollection",
        "features": []
    }

    # The input data is a list of annotations
    for annotation_item in data:
        # Check if the required keys exist
        if "annotation" not in annotation_item or "elements" not in annotation_item["annotation"]:
            print(f"Skipping an item due to missing 'annotation' or 'elements' key: {annotation_item.get('_id')}")
            continue

        # Iterate through each geometric element in the annotation
        for element in annotation_item['annotation']['elements']:
            if element.get('type') == 'polyline' and 'points' in element:
                # Extract coordinates, removing the Z-value (the 3rd element)
                # GeoJSON uses (x, y) coordinates.
                coordinates = [point[:2] for point in element['points']]

                # Ensure the polygon is closed by making sure the first and last points are the same
                if element.get('closed') and coordinates and coordinates[0] != coordinates[-1]:
                    coordinates.append(coordinates[0])

                # Create the geometry for the GeoJSON feature.
                # For a closed polyline, this is a Polygon.
                geometry = {
                    "type": "Polygon",
                    "coordinates": [coordinates] # Polygons require a list of linear rings.
                }

                # Set up the properties for the feature, including styling
                # and any other metadata from the source.
                properties = {
                    "id": element.get('id'),
                    "lineColor": element.get('lineColor'),
                    "fillColor": element.get('fillColor'),
                    "lineWidth": element.get('lineWidth')
                }

                # Create the final GeoJSON Feature object
                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": properties
                }

                # Add the feature to our collection
                geojson_output['features'].append(feature)

    # Write the complete GeoJSON object to the output file
    try:
        with open(output_filename, 'w') as f:
            json.dump(geojson_output, f, indent=2)
        print(f"Successfully converted '{input_filename}' to '{output_filename}'")
    except IOError:
        print(f"Error: Could not write to the file '{output_filename}'.")


if __name__ == '__main__':
    # --- Instructions for use ---
    # This script is designed to be run from the command line.
    #
    # Usage:
    # python your_script_name.py <input_json_file> <output_geojson_file>
    #
    # Example:
    # python converter.py N20_annotations.json N20_output.geojson
    
    parser = argparse.ArgumentParser(
        description="Converts a specific JSON annotation format to Aperio-compatible GeoJSON."
    )
    parser.add_argument(
        "input_file", 
        help="The path to the input JSON annotation file."
    )
    parser.add_argument(
        "output_file", 
        help="The path for the output GeoJSON file."
    )
    
    args = parser.parse_args()
    
    convert_to_aperio_geojson(args.input_file, args.output_file)

