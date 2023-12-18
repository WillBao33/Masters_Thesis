import numpy as np
import rasterio
import networkx as nx
import csv
from skimage.morphology import skeletonize, dilation, square, erosion
import os

sidewalk_cost = 0.5
crosswalk_cost = 0.5
# Transformation function to scale down the pixel coordinates
# def transform_to_gazebo_coordinates(pixel_coord):
#     y, x = pixel_coord
    
#     # Scaling down by the given factor
#     gazebo_x = x / scale_factor
#     gazebo_y = y / scale_factor
    
#     return (gazebo_x, gazebo_y)

def gps_to_pixel(lon, lat, dataset):
    row, col = dataset.index(lon, lat)
    return row, col

def euclidean_distance(node1, node2):
    (y1, x1) = node1
    (y2, x2) = node2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def manhattan_distance(node1, node2):
    (y1, x1) = node1
    (y2, x2) = node2
    return abs(x1 - x2) + abs(y1-y2)

# def compute_path_energy(path, graph, distance_func,w1,w2):
#     total_energy = 0
#     total_safety_score = 0
#     sidewalk_count = 0
#     crosswalk_count = 0


#     for i in range(len(path) - 1):
#         node1 = path[i]
#         node2 = path[i + 1]

#         distance = distance_func(node1, node2)
#         weight = graph.nodes[node1]['weight']

#         # Calculate safety score based on weight (i.e., type of terrain)
#         if weight == sidewalk_cost:  # Assume 0.5 is the weight for sidewalks
#             safety_score = 1  # Assume sidewalks are safest; you can change this value
#             sidewalk_count += 1
#         elif weight == crosswalk_cost:  # Assume 30.0 is the weight for crosswalks
#             safety_score = 0  # Assume crosswalks are less safe; you can change this value
#             crosswalk_count += 1
#         else:
#             safety_score = 0  # Default value for any other type of terrain

#         # Incorporate safety score into the energy function
#         segment_energy = w1*distance+w2*(1-safety_score)
#         total_energy += segment_energy


#     # If you want to return the proportion of sidewalk and crosswalk
#     total_count = sidewalk_count + crosswalk_count
#     sidewalk_ratio = sidewalk_count / total_count if total_count != 0 else 0
#     crosswalk_ratio = crosswalk_count / total_count if total_count != 0 else 0

#     return total_energy, sidewalk_ratio, crosswalk_ratio

def compute_path_energy(path, graph, distance_func, weights):
    results = []
    for w1, w2 in weights:
        total_energy = 0
        sidewalk_count = 0
        crosswalk_count = 0

        for i in range(len(path) - 1):
            node1 = path[i]
            node2 = path[i + 1]

            distance = distance_func(node1, node2)
            weight = graph.nodes[node1]['weight']

            if weight == sidewalk_cost:
                safety_score = 1
                sidewalk_count += 1
            elif weight == crosswalk_cost:
                safety_score = 0
                crosswalk_count += 1
            else:
                safety_score = 0

            segment_energy = w1 * distance + w2 * (1 - safety_score)
            total_energy += segment_energy

        total_count = sidewalk_count + crosswalk_count
        sidewalk_ratio = sidewalk_count / total_count if total_count != 0 else 0
        crosswalk_ratio = crosswalk_count / total_count if total_count != 0 else 0

        results.append((total_energy, sidewalk_ratio, crosswalk_ratio, w1, w2))

    return results


# Read the GeoTIFF and process the image
with rasterio.open('concat_all.tif') as dataset:  # binary sidewalk and crosswalk network image
    array = dataset.read(1)
    #array = erosion(array, square(7))
    cost_array = np.where(array == 255, sidewalk_cost, np.where(array == 128, crosswalk_cost, np.inf))
    navigable_pixels = np.isfinite(cost_array)

    # Skeletonize navigable pixels
    skeleton = skeletonize(navigable_pixels) # shrink down pixel width

    # Define start and end point in GPS coordinates
    start_lon, start_lat = -8783043.932, 5457265.278  # Replace with your start coordinates
    end_lon, end_lat = -8778264.198, 5456317.822  # Replace with your end coordinates

    # Convert start and end point to pixel coordinates
    start_row, start_col = gps_to_pixel(start_lon, start_lat, dataset)
    end_row, end_col = gps_to_pixel(end_lon, end_lat, dataset)

    G = nx.Graph()

    # Only add valid (non-black) pixels as nodes
    # Prefer the skeletonized pixels
    for y in range(cost_array.shape[0]):
        for x in range(cost_array.shape[1]):
            if navigable_pixels[y][x]:
                weight = cost_array[y][x]
                if skeleton[y][x]:
                    weight = weight * 0.1  # Lower weight for skeletonized pixels
                G.add_node((y, x), weight=weight)

    # Add edges between each node and its neighbors
    for y in range(cost_array.shape[0]):
        for x in range(cost_array.shape[1]):
            if navigable_pixels[y][x]:
                current_weight = G.nodes[(y, x)]['weight']
                if y > 0 and navigable_pixels[y - 1][x]:
                    upper_weight = G.nodes[(y - 1, x)]['weight']
                    G.add_edge((y, x), (y - 1, x), weight=0.5 * (current_weight + upper_weight))
                if y < cost_array.shape[0] - 1 and navigable_pixels[y + 1][x]:
                    lower_weight = G.nodes[(y + 1, x)]['weight']
                    G.add_edge((y, x), (y + 1, x), weight=0.5 * (current_weight + lower_weight))
                if x > 0 and navigable_pixels[y][x - 1]:
                    left_weight = G.nodes[(y, x - 1)]['weight']
                    G.add_edge((y, x), (y, x - 1), weight=0.5 * (current_weight + left_weight))
                if x < cost_array.shape[1] - 1 and navigable_pixels[y][x + 1]:
                    right_weight = G.nodes[(y, x + 1)]['weight']
                    G.add_edge((y, x), (y, x + 1), weight=0.5 * (current_weight + right_weight))

    # Define start and end nodes
    start_node = (start_row, start_col)
    end_node = (end_row, end_col)

    # Compute shortest path
    path = nx.astar_path(G, start_node, end_node, heuristic=None, weight='weight')
    print("Total nodes (steps) in the path:", len(path))

    # Calculate the Actual Distance
    resolution_x, resolution_y = dataset.res
    total_distance = 0.0
    for i in range(1, len(path)):
        (y1, x1) = path[i-1]
        (y2, x2) = path[i]
        pixel_distance = euclidean_distance((y1, x1), (y2, x2))  # Euclidean distance in pixels
        actual_distance = pixel_distance * max(resolution_x, resolution_y)  # Convert to actual distance
        total_distance += actual_distance
    print(f"Total distance: {total_distance} meters")

    #total_energy,sidewalk_ratio,crosswalk_ratio = compute_path_energy(path,G,euclidean_distance,w1,w2)
    
    weights = [(0.5, 0.5), (0.9, 0.1), (0.1, 0.9)]
    all_results = compute_path_energy(path, G, euclidean_distance, weights)
    print(f"Total energy of the path: {all_results[0]}")

    file_exists = os.path.isfile('thesis/results_paper.csv')
    
    with open('thesis/results_paper.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
    # Write the 
        if not file_exists:
            csvwriter.writerow(['Total Nodes', 'Total Distance(m)', 'Heuristic', 'Cost for Sidewalk', 'Cost for Crosswalk', 'Total Energy','Sidewalk Ratio','Crosswalk Ratio','w1','w2'])
    # Write the data
        for result in all_results:
            total_energy, sidewalk_ratio, crosswalk_ratio, w1, w2 = result
            csvwriter.writerow([len(path), round(total_distance, 2), 'None', sidewalk_cost, crosswalk_cost, total_energy, round(sidewalk_ratio, 2), round(crosswalk_ratio, 2), w1, w2])

    # Convert grayscale to RGB
    rgb_array = np.stack([array, array, array], axis=-1)

    # Draw the path on the original image data
    for node in path:
        rgb_array[node] = [255, 0, 0]  # or other value that stands out

    # Use the metadata from the original dataset
    metadata = dataset.meta
    metadata.update(count=3)

    # Save as a new GeoTIFF file
    with rasterio.open(f'thesis/without_heuristic_{crosswalk_cost}_{round(total_distance,2)}m.tif', 'w', **metadata) as dst:
        for band in range(3):
            dst.write(rgb_array[:, :, band], band + 1)
        # List to hold the waypoints
    # waypoints = []
    #     # Constants
    # scale_factor = 100


    # # Iterate over the path, transforming and scaling the coordinates
    # for node in path:
    #     gazebo_coord = transform_to_gazebo_coordinates(node)
    #     waypoints.append(gazebo_coord)

    # with open('thesis/waypoints.csv', 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(waypoints)


    # Now waypoints contain the (x, y) coordinates in Gazebo's world frame
    # print("Waypoints for Gazebo:", waypoints)
