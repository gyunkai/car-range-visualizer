# EV Range Visualization

A Python prototype that calculates and visualizes the maximum reachable area for an electric vehicle (EV) based on a given starting point and remaining battery range. This tool uses real navigation-based distances rather than simple radius-based estimations.

## Features

- Fetch real driving distances using OpenRouteService API (or optionally Google Maps API)
- Compute reachable area based on EV battery range
- Generate a polygon representing the reachable area
- Render the polygon on an interactive map using Folium

## Environment Setup

### Setting Up a Virtual Environment

It's recommended to use a virtual environment to avoid conflicts with other Python projects. Here's how to set it up:

```bash
# Create a virtual environment
conda create -n ev_range python=3.10

# Activate the virtual environment
conda activate ev_range
```

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/gyunkai/car-range-visualizer.git
   cd car-range-visualizer
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up API keys:

   ```bash
   # Copy the template environment file
   cp .env.template .env

   # Edit .env file with your API keys
   # Get your OpenRouteService API key from: https://openrouteservice.org/dev/#/signup
   # (Optional) Get your Google Maps API key from: https://console.cloud.google.com/google/maps-apis/credentials
   ```

4. Verify installation:

   ```bash
   # Run the test suite
   python src/test.py

   # Try the example script
   python src/example.py
   ```

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys:
   ```
   ORS_API_KEY=your_openrouteservice_api_key
   GOOGLE_API_KEY=your_google_maps_api_key  # Optional
   ```
4. Run the main script: `python src/main.py`

## Usage

### Command Line Interface

You can use the tool from the command line with the following options:

```bash
# Basic usage with required parameters
python src/main.py --lat 52.5200 --lon 13.4050 --range 150

# Extended example with all options
python src/main.py --lat 52.5200 --lon 13.4050 --range 150 --buffer 15 --directions 24 --output berlin_range.html

# Using Google Maps API instead of OpenRouteService
python src/main.py --lat 37.7749 --lon -122.4194 --range 200 --use-google
```

Command line options:

- `--lat`: Starting latitude (required)
- `--lon`: Starting longitude (required)
- `--range`: Battery range in kilometers (required)
- `--buffer`: Safety buffer in kilometers (default: 10)
- `--directions`: Number of directions to check (default: 16, higher values create smoother polygons)
- `--use-google`: Use Google Maps API instead of OpenRouteService
- `--output`: Output HTML file path (default: ev_range_map.html)

### Python API

You can also use the EVRangeVisualizer class directly in your Python code:

```python
from ev_range import EVRangeVisualizer

# Initialize with a starting location
visualizer = EVRangeVisualizer(
    start_location=(52.5200, 13.4050),  # Berlin coordinates
    battery_range=150,  # km
    efficiency_buffer=10,  # km
    num_directions=16,  # Number of directions to check (higher = smoother polygon)
    use_google=False  # Use OpenRouteService API (default)
)

# Generate the range visualization
visualizer.generate_range_map()

# Save the map
visualizer.save_map("ev_range_map.html")
```

### Example Locations

The repository includes a sample script that demonstrates visualizing the range from Berlin:

```bash
python src/example.py
```

You can modify the `example.py` script to use different locations:

```python
# Available example locations:
# - "San Francisco": (37.7749, -122.4194)
# - "New York": (40.7128, -74.0060)
# - "London": (51.5074, -0.1278)
# - "Tokyo": (35.6762, 139.6503)
# - "Berlin": (52.5200, 13.4050)

# In the main() function, change:
location_name = "San Francisco"  # Change to any of the above cities
```

### Output

The tool generates an interactive HTML map that can be opened in any web browser. The map shows:

1. The starting location (green marker)
2. The boundary points calculated in each direction (blue dots)
3. A blue polygon representing the maximum reachable area

The interactive map allows zooming, panning, and clicking on markers to see additional information.

### Running Tests

To verify that the tool is working correctly, you can run the included unit tests:

```bash
python src/test.py
```

## API Keys

- **OpenRouteService API** (default): Get a free key from [openrouteservice.org/dev/#/signup](https://openrouteservice.org/dev/#/signup)
- **Google Maps API** (optional): Get a key from [console.cloud.google.com](https://console.cloud.google.com/google/maps-apis/credentials)

## Requirements

See `requirements.txt` for a list of dependencies.

## License

MIT
