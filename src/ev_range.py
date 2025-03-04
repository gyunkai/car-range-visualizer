import os
import math
import folium
import numpy as np
import openrouteservice as ors
import requests
from shapely.geometry import Polygon, Point
from geopy.distance import geodesic
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EVRangeVisualizer:
    """
    A class to visualize the maximum reachable area for an electric vehicle
    based on battery range and starting location.
    """
    
    def __init__(self, start_location, battery_range, efficiency_buffer=10, 
                 num_directions=16, use_google=False):
        """
        Initialize the EVRangeVisualizer.
        
        Args:
            start_location (tuple): (latitude, longitude) of starting point
            battery_range (float): Maximum distance the EV can travel (km)
            efficiency_buffer (float): Safety buffer to subtract from range (km)
            num_directions (int): Number of directions to check for range
            use_google (bool): Whether to use Google Maps API instead of OpenRouteService
        """
        self.start_location = start_location
        self.battery_range = battery_range
        self.efficiency_buffer = efficiency_buffer
        self.effective_range = battery_range - efficiency_buffer
        self.num_directions = num_directions
        self.use_google = use_google
        
        # Initialize API clients
        if use_google:
            self.google_api_key = os.getenv('GOOGLE_API_KEY')
            if not self.google_api_key:
                raise ValueError("Google API key not found. Set GOOGLE_API_KEY in .env file.")
        else:
            self.ors_api_key = os.getenv('ORS_API_KEY')
            if not self.ors_api_key:
                raise ValueError("OpenRouteService API key not found. Set ORS_API_KEY in .env file.")
            self.ors_client = ors.Client(key=self.ors_api_key)
        
        # Initialize map objects
        self.boundary_points = []
        self.range_polygon = None
        self.map = None
    
    def _calculate_destination_point(self, azimuth, distance_km):
        """
        Calculate a destination point given a starting point, azimuth, and distance.
        
        Args:
            azimuth (float): Direction angle in degrees (0=North, 90=East, etc.)
            distance_km (float): Distance to travel in kilometers
            
        Returns:
            tuple: (latitude, longitude) of destination point
        """
        # Get approximate destination for API query
        start_point = Point(self.start_location[1], self.start_location[0])  # lon, lat
        
        # Convert km to degrees (very rough approximation to get a distant enough point)
        # This is just to get a point for the API query, not for accurate distance calculation
        lat_deg = distance_km / 111.0  # 1 degree latitude is approximately 111 km
        # Adjust longitude degrees based on latitude
        lon_deg = distance_km / (111.0 * math.cos(math.radians(self.start_location[0])))
        
        # Calculate offset
        dx = lon_deg * math.sin(math.radians(azimuth))
        dy = lat_deg * math.cos(math.radians(azimuth))
        
        # Calculate destination coordinates
        dest_lon = self.start_location[1] + dx
        dest_lat = self.start_location[0] + dy
        
        return (dest_lat, dest_lon)
    
    def _get_routable_distance_openrouteservice(self, dest):
        """
        Get the actual routable distance to a destination using OpenRouteService API.
        
        Args:
            dest (tuple): (latitude, longitude) of destination
            
        Returns:
            float: Distance in kilometers, or None if route not found
        """
        try:
            # Request route from OpenRouteService
            coords = [[self.start_location[1], self.start_location[0]], 
                      [dest[1], dest[0]]]
            
            route = self.ors_client.directions(
                coordinates=coords,
                profile='driving-car',
                format='geojson'
            )
            
            # Extract distance from route
            return route['features'][0]['properties']['summary']['distance'] / 1000  # Convert meters to km
        except Exception as e:
            print(f"Error calculating route: {e}")
            return None
    
    def _get_routable_distance_google(self, dest):
        """
        Get the actual routable distance to a destination using Google Maps Directions API.
        
        Args:
            dest (tuple): (latitude, longitude) of destination
            
        Returns:
            float: Distance in kilometers, or None if route not found
        """
        try:
            # Build URL for Google Maps Directions API
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": f"{self.start_location[0]},{self.start_location[1]}",
                "destination": f"{dest[0]},{dest[1]}",
                "key": self.google_api_key
            }
            
            # Make API request
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                # Extract distance from route
                distance_meters = data['routes'][0]['legs'][0]['distance']['value']
                return distance_meters / 1000  # Convert meters to km
            return None
        except Exception as e:
            print(f"Error calculating route: {e}")
            return None
    
    def _find_boundary_point(self, azimuth):
        """
        Find the furthest reachable point in a given direction using binary search.
        
        Args:
            azimuth (float): Direction angle in degrees
            
        Returns:
            tuple: (latitude, longitude) of boundary point, or None if not found
        """
        min_distance = 0
        max_distance = self.effective_range * 1.5  # Start with a slightly larger search space
        best_point = None
        best_distance = 0
        
        for _ in range(10):  # Max 10 iterations of binary search
            mid_distance = (min_distance + max_distance) / 2
            dest_point = self._calculate_destination_point(azimuth, mid_distance)
            
            # Get actual routable distance
            if self.use_google:
                actual_distance = self._get_routable_distance_google(dest_point)
            else:
                actual_distance = self._get_routable_distance_openrouteservice(dest_point)
            
            if actual_distance is None:
                max_distance = mid_distance
                continue
                
            if actual_distance <= self.effective_range:
                # This point is reachable, try further
                min_distance = mid_distance
                if actual_distance > best_distance:
                    best_distance = actual_distance
                    best_point = dest_point
            else:
                # This point is too far, try closer
                max_distance = mid_distance
        
        return best_point
    
    def generate_range_map(self):
        """
        Generate a map showing the maximum range of the EV from the starting point.
        """
        print("Generating EV range map...")
        
        # Clear previous data
        self.boundary_points = []
        
        # Calculate boundary points in different directions
        angles = np.linspace(0, 360, self.num_directions, endpoint=False)
        
        for angle in tqdm(angles, desc="Finding boundary points"):
            boundary_point = self._find_boundary_point(angle)
            if boundary_point:
                self.boundary_points.append(boundary_point)
        
        # Create a polygon from boundary points
        if len(self.boundary_points) >= 3:
            self.range_polygon = Polygon([(point[1], point[0]) for point in self.boundary_points])
        else:
            print("Not enough boundary points found to create a polygon")
            return
        
        # Create a map centered at the starting point
        self.map = folium.Map(location=self.start_location, zoom_start=10)
        
        # Add starting point marker
        folium.Marker(
            location=self.start_location,
            popup=f"Start: ({self.start_location[0]:.4f}, {self.start_location[1]:.4f})",
            icon=folium.Icon(color='green', icon='car', prefix='fa')
        ).add_to(self.map)
        
        # Add range polygon
        folium.GeoJson(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [point[1], point[0]] for point in self.boundary_points
                    ]]
                },
                "properties": {
                    "name": f"EV Range ({self.battery_range} km)",
                    "style": {
                        "fillColor": "#3388ff",
                        "color": "#3388ff",
                        "weight": 2,
                        "fillOpacity": 0.4
                    }
                }
            }
        ).add_to(self.map)
        
        # Add boundary points markers
        for i, point in enumerate(self.boundary_points):
            folium.CircleMarker(
                location=point,
                radius=4,
                color='blue',
                fill=True,
                fill_color='blue',
                popup=f"Boundary Point {i+1}: ({point[0]:.4f}, {point[1]:.4f})"
            ).add_to(self.map)
        
        print(f"Range map generated with {len(self.boundary_points)} boundary points")
        return self.map
    
    def save_map(self, filename):
        """
        Save the generated map to an HTML file.
        
        Args:
            filename (str): Name of the HTML file to save
        """
        if self.map is None:
            print("No map to save. Run generate_range_map() first.")
            return
        
        self.map.save(filename)
        print(f"Map saved to {filename}") 