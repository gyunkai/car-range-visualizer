#!/usr/bin/env python3
"""
EV Range Visualization - Main Script

This script demonstrates how to use the EVRangeVisualizer to calculate and 
visualize the range of an electric vehicle based on battery range and starting location.
"""

import argparse
import os
from dotenv import load_dotenv
from ev_range import EVRangeVisualizer

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EV Range Visualization Tool')
    
    parser.add_argument('--lat', type=float, required=True,
                        help='Starting latitude')
    parser.add_argument('--lon', type=float, required=True,
                        help='Starting longitude')
    parser.add_argument('--range', type=float, required=True,
                        help='Battery range in kilometers')
    parser.add_argument('--buffer', type=float, default=10,
                        help='Safety buffer in kilometers (default: 10)')
    parser.add_argument('--directions', type=int, default=16,
                        help='Number of directions to check (default: 16)')
    parser.add_argument('--use-google', action='store_true',
                        help='Use Google Maps API instead of OpenRouteService')
    parser.add_argument('--output', type=str, default='ev_range_map.html',
                        help='Output HTML file (default: ev_range_map.html)')
    
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    # Create the visualizer
    visualizer = EVRangeVisualizer(
        start_location=(args.lat, args.lon),
        battery_range=args.range,
        efficiency_buffer=args.buffer,
        num_directions=args.directions,
        use_google=args.use_google
    )
    
    # Generate the range map
    visualizer.generate_range_map()
    
    # Save the map
    visualizer.save_map(args.output)
    
    print(f"EV range map saved to {args.output}")
    print(f"Open this file in a web browser to view the visualization.")

if __name__ == '__main__':
    main() 