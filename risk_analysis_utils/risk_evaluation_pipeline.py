"""
Script Purpose:
    Parse obstacle statistics from JSON files in a user-specified folder, summarize the obstacles by distance and type, display the results in a rich table, and save a text file listing which files had obstacles in each distance range.

Step-by-Step Logic:

1. Prompt for Folder Path
    - Ask the user to input the path to the folder containing the JSON files.

2. Iterate Over JSON Files
    - For each `.json` file in the folder:
        - Open and parse the file.
        - Check for the `obstacles` key (should be a list).

3. Extract Obstacle Data
    - For each obstacle in the list:
        - Get the `distance` (when the obstacle was first detected).
        - Get the `type` (e.g., "higher", "dropoff").

4. Bin Obstacles by Distance
    - Define distance bins: 0–0.5m, 0.5–1.0m, ..., 3.5–4.0m.
    - For each obstacle, determine which bin its distance falls into.
    - Count the number of obstacles of each type in each bin.
    - Keep track of which files had obstacles in each bin.

5. Display Results with Rich Table
    - Use the `rich` library to display a table:
        - Rows: Distance bins (e.g., "0–0.5m", "0.5–1.0m", etc.)
        - Columns: Obstacle types (e.g., "higher", "dropoff"), and total count.
        - Each cell: Number of obstacles of that type in that bin.

6. Save File List by Bin
    - For each distance bin, create a text file (e.g., `bin_0-0.5m.txt`) listing the names of all JSON files where obstacles were detected in that bin.

How to Make the Logic Understandable:
    - Use clear variable names (e.g., `distance_bins`, `obstacle_counts`, `files_by_bin`).
    - Add comments explaining each step.
    - Use functions for each logical part (e.g., `get_json_files`, `parse_obstacles`, `bin_obstacles`, `display_table`, `save_file_lists`).
    - Print helpful messages for the user (e.g., "Parsing file X...", "No obstacles found in file Y.").
"""
