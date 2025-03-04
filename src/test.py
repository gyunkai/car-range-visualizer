#!/usr/bin/env python3
"""
Test script for the EVRangeVisualizer

This script creates a simple test case using a mock API response
to verify that the EVRangeVisualizer works correctly.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from ev_range import EVRangeVisualizer

class TestEVRangeVisualizer(unittest.TestCase):
    """Test cases for the EVRangeVisualizer."""
    
    @patch('openrouteservice.Client')
    def test_initialization(self, mock_client):
        """Test that the visualizer initializes correctly."""
        # Mock environment variable
        with patch.dict(os.environ, {"ORS_API_KEY": "fake_key"}):
            visualizer = EVRangeVisualizer(
                start_location=(52.5200, 13.4050),
                battery_range=150,
                efficiency_buffer=10
            )
            
            self.assertEqual(visualizer.start_location, (52.5200, 13.4050))
            self.assertEqual(visualizer.battery_range, 150)
            self.assertEqual(visualizer.efficiency_buffer, 10)
            self.assertEqual(visualizer.effective_range, 140)
            self.assertEqual(visualizer.num_directions, 16)
            self.assertFalse(visualizer.use_google)
    
    @patch('openrouteservice.Client')
    def test_calculate_destination_point(self, mock_client):
        """Test destination point calculation."""
        with patch.dict(os.environ, {"ORS_API_KEY": "fake_key"}):
            visualizer = EVRangeVisualizer(
                start_location=(52.5200, 13.4050),
                battery_range=100
            )
            
            # Test North (0 degrees)
            north_point = visualizer._calculate_destination_point(0, 10)
            self.assertAlmostEqual(north_point[0], 52.6100, places=3)
            self.assertAlmostEqual(north_point[1], 13.4050, places=3)
            
            # Test East (90 degrees)
            east_point = visualizer._calculate_destination_point(90, 10)
            self.assertAlmostEqual(east_point[0], 52.5200, places=3)
            self.assertAlmostEqual(east_point[1], 13.5310, places=2)
    
    @patch('openrouteservice.Client')
    def test_get_routable_distance(self, mock_client):
        """Test distance calculation using mocked API response."""
        # Mock the API response
        mock_instance = mock_client.return_value
        mock_instance.directions.return_value = {
            'features': [{
                'properties': {
                    'summary': {
                        'distance': 12500  # 12.5 km in meters
                    }
                }
            }]
        }
        
        with patch.dict(os.environ, {"ORS_API_KEY": "fake_key"}):
            visualizer = EVRangeVisualizer(
                start_location=(52.5200, 13.4050),
                battery_range=100
            )
            
            dest = (52.6100, 13.4050)
            distance = visualizer._get_routable_distance_openrouteservice(dest)
            
            # Check if distance is correctly calculated
            self.assertEqual(distance, 12.5)
            
            # Verify API was called with correct parameters
            mock_instance.directions.assert_called_once()
            args, kwargs = mock_instance.directions.call_args
            self.assertEqual(kwargs['profile'], 'driving-car')
            self.assertEqual(kwargs['format'], 'geojson')
            self.assertEqual(kwargs['coordinates'][0], [13.4050, 52.5200])
            self.assertEqual(kwargs['coordinates'][1], [13.4050, 52.6100])

def main():
    """Run the tests."""
    unittest.main()

if __name__ == '__main__':
    main() 