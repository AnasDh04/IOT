from django.shortcuts import render # pour la reponce en html
from django.http import HttpResponse # pour la reponse en httpresponse
from django.http import JsonResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
from math import sqrt
from IPython.display import display
import json
from django.http import JsonResponse

# cette fonction fait reference a ce qui doit etre afficher au sein d elle ok 
def say_hello(request): 
#la nature de reponce envoyer
    return render(request ,'hello.html')

# Django view example to retrieve temperature data from MongoDB Atlas



def get_temperature_data(request):
    # Replace the following with your MongoDB connection details
    client = MongoClient('mongodb+srv://hiba99:marwa2020@cluster0.ji3zoyq.mongodb.net/dht11?retryWrites=true&w=majority')
    db = client['dht11']
    collection = db['locations']
    
    # Retrieving the last 6 data points for the example
     # Replace 'your_streamname_id' with the ObjectId from your image
    streamname_id = ObjectId('65afebfa3a22637b465ed298')

    # Retrieve the last 4 documents where 'streamname' matches 'streamname_id'
    temperature_data = collection.find({'Streamname': streamname_id}).sort('_id', 1)

    # Transforming the data into the format expected by Chart.js
    hh = [([datetime.fromisoformat(data['PhenomenonTime']).strftime("%H:%M") ,data['Result']])for data in temperature_data]
    transformed_list = [[item[0] for item in hh], [item[1] for item in hh]]


    # temperatures = [data['Result'] for data in temperature_data]
   
    data = {
        # 'labels': ["9AM", "10AM", "11AM", "12PM"],
       'labels': transformed_list[0],
        'datasets': [{
            'label': 'Temperature',
            'data': transformed_list[1],
            # You can add more styling options here
        }]
    }
    return JsonResponse(data)

def display_merchandise(request):

    client = MongoClient('mongodb+srv://hiba99:marwa2020@cluster0.ji3zoyq.mongodb.net/dht11?retryWrites=true&w=majority')
    db = client['dht11']
    collection = db['locations']
   
    streamname_id = ObjectId('65b022c795741b787cf07f91')
    
    location_data = collection.find({'_id': streamname_id})
    if location_data:
        coordinates = [data['Location']['coordinates'] for data in location_data]
    loc = {       
            'x': coordinates[0][1],
            'y': coordinates[0][0],
    }
    return JsonResponse(loc)

# def display_shelves_centroids(room):


#     streamname_id = ObjectId('65b022c795741b787cf07f91')



def display_shelves_centroids(request):
    input_file = 'C:\IOT\sS.geojson'

    # Read the GeoJSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Filter points with status = 1 and rooms = given room
    filtered_features = [feature for feature in data['features'] if feature['properties']['status'] == 1 and feature['properties']['rooms'] == 'B']

    # Extract shelves information from filtered features
    shelves = []
    for feature in filtered_features:
        shelves.append({
            'label': feature['properties']['id'],
            'coordinates': {
                'x': feature['geometry']['coordinates'][1],
                'y': feature['geometry']['coordinates'][0],
            }
        })

    return JsonResponse(shelves, safe=False)

def routing(request):
    
    client = MongoClient('mongodb+srv://hiba99:marwa2020@cluster0.ji3zoyq.mongodb.net/dht11?retryWrites=true&w=majority')
    db = client['dht11']
    collection = db['thing_locations']
    coll_loc=db['locations']
    coll_thing=db['things']
    # Retrieve the last 4 documents where 'streamname' matches 'streamname_id'
    last_thing = collection.find().sort('_id', -1).limit(1)
    # Transforming the data into the format expected by Chart.js
    obj_location_id = [(data['id_location'] ,data['id_thing'])for data in last_thing]

    obj_location_id=obj_location_id[0]

    obj_location_id,obj_thing_id =obj_location_id[0],obj_location_id[1]


    last_thing_loca = coll_loc.find({'Description': str(obj_location_id)})

    # Transforming the data into the format expected by Chart.js
    obj_location = [data['Location'] for data in last_thing_loca]
    obj_location =obj_location[0]['coordinates']
    #########################################
    # Retrieve the last 4 documents where 'streamname' matches 'streamname_id'
    obj_thing = coll_thing.find({'_id': ObjectId(obj_thing_id)})

    # Transforming the data into the format expected by Chart.js
    obj_thingy = [data['Properties']['room'] for data in obj_thing]
    obj_thingy=obj_thingy[0]
    obj_thingy=obj_thingy.split(' ')[1]
    print('location',obj_location)
    print('room',obj_thingy)


    
    
    
    
    
    
    def load_geojson_segments(file_path):
        """Load segments from a GeoJSON file."""
        gdf = gpd.read_file(file_path)
        if not gdf.empty:
            return gdf
        else:
            raise ValueError("GeoJSON file is empty or not valid.")

    def extract_start_end_points(gdf):
        """Extract start and end points from each LineString segment."""
        points_list = []
        for idx, row in gdf.iterrows():
            if isinstance(row.geometry, LineString):
                start_point = Point(row.geometry.coords[0])
                end_point = Point(row.geometry.coords[-1])
                points_list.append((start_point, end_point))
            else:
                print(f"Row {idx} is not a LineString.")
        return points_list

    def calc_distance(point1, point2):
        """Calculate distance between two points."""
        return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    # Load the segments from the GeoJSON file
    segments_gdf = load_geojson_segments('C:/IOT/RootingFinalF.geojson')

    # Extract start and end points
    points_list = extract_start_end_points(segments_gdf)

    # Create a directed graph
    G = nx.DiGraph()

    # Add edges to the graph along with their weights (distances)
    for start, end in points_list:
        distance = calc_distance((start.y, start.x), (end.y, end.x))
        G.add_edge((start.y, start.x), (end.y, end.x), weight=distance)
        G.add_edge((end.y, end.x), (start.y, start.x), weight=distance)  # If the paths are bidirectional

    shortest_paths = []  # Store all shortest paths to different end points
    min_distance = float('inf')  # Initialize with a very large value
    closest_shortest_path = None  # Initialize closest_shortest_path outside the loop
    
    input_file = 'C:/IOT/sS.geojson'

    # Read the GeoJSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Filter points with status = 1 and rooms = given room
    filtered_features = [feature for feature in data['features'] if feature['properties']['status'] == 1 and feature['properties']['rooms'] == obj_thingy]

    # Extract shelves information from filtered features
    shelves = []
    for feature in filtered_features:
        shelves.append({
            'label': feature['properties']['id'],
            'coordinates': {
                'x': feature['geometry']['coordinates'][1],
                'y': feature['geometry']['coordinates'][0],
            }
        })

    coordinates_list = [(feature["coordinates"]["x"], feature["coordinates"]["y"]) for feature in shelves]  # Populate coordinates_list here
    
    for end_point in coordinates_list:
        
        
        start_point = obj_location
        # Find the nearest points in the graph to the provided start and end points
        start_node = min(G.nodes(), key=lambda x: calc_distance(x, start_point))
        end_node = min(G.nodes(), key=lambda x: calc_distance(x, end_point))

        # Check if start and end nodes are within the range of the road network
        if start_node not in G or end_node not in G:
            print("Start or end point is not within the road network.")
        else:
            # Find the shortest path using Dijkstra's algorithm
            try:
                shortest_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
                shortest_paths.append(shortest_path)
                distance_to_end_point = sum(calc_distance(shortest_path[i], shortest_path[i+1]) for i in range(len(shortest_path)-1))
                if distance_to_end_point < min_distance:
                    min_distance = distance_to_end_point
                    closest_shortest_path = shortest_path
                    
            except nx.NetworkXNoPath:
                print("No path found between the provided start and end points.")
                
    return JsonResponse(closest_shortest_path, safe=False)
