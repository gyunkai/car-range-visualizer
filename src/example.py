#!/usr/bin/env python3
"""
Example script showing how to use the EVRangeVisualizer programmatically
"""

from ev_range import EVRangeVisualizer

# Example locations
LOCATIONS = {
    "San Francisco": (37.7749, -122.4194),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
    "Berlin": (52.5200, 13.4050),
}

def main():
    """Run an example EV range visualization for Berlin."""
    
    # Select a location
    location_name = "Berlin"
    start_location = LOCATIONS[location_name]
    
    # Set up configuration
    battery_range = 150  # km
    efficiency_buffer = 10  # km
    
    print(f"Calculating EV range for {location_name} with {battery_range} km range...")
    
    # Create visualizer
    visualizer = EVRangeVisualizer(
        start_location=start_location,
        battery_range=battery_range,
        efficiency_buffer=efficiency_buffer,
        num_directions=24,  # More directions for smoother polygon
        use_google=False  # Use OpenRouteService API
    )
    
    # Generate map
    visualizer.generate_range_map()
    
    # Save result
    output_file = f"ev_range_{location_name.lower()}.html"
    visualizer.save_map(output_file)
    
    print(f"Range map saved to {output_file}")
    print("Open this file in a web browser to view the visualization.")

if __name__ == "__main__":
    main() 