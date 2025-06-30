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

import os
import numpy as np
import json


class RiskEvaluationPipeline:
    def __init__(self, evaluation_dir, max_distance=4.0, resolution=0.5):
        self.evaluation_dir = evaluation_dir
        self._n_videos = len([f for f in os.listdir(evaluation_dir) if f.endswith(".json")])

        self._count_obstacle_free = 0
        self._count_both_type = 0
        self._resolution = resolution

        self._num_bins = int(max_distance / resolution)
        self.higher_obstacle_bins = np.zeros(self._num_bins, dtype=np.int16)
        self.dropoff_bins = np.zeros(self._num_bins, dtype=np.int16)
        self.higher_obstacles_bin_files = {n: [] for n in range(self._num_bins)}
        self.dropoff_bins_files = {n: [] for n in range(self._num_bins)}
        self.dropoff_higher_obstacle = []

        self.obstacle_free_file_names = []

        self.results_dir = None

    def run(self):
        pass

    def _run_evaluation(self):
        for file in os.listdir(self.evaluation_dir):
            if not file.endswith(".json"):
                continue
            file_path = os.path.join(self.evaluation_dir, file)
            with open(file_path, "r") as f:
                data = json.load(f)

                if not data["obstacles"]:
                    self._count_obstacle_free += 1
                    self.obstacle_free_file_names.append(data["name"])
                    continue

                for obstacle in data["obstacles"]:
                    distance = obstacle["distance"]
                    bin_index = int(distance // self._resolution)
                    if bin_index >= self._num_bins:
                        bin_index = self._num_bins - 1
                    if obstacle["is_higher_obstacle"] and not obstacle["is_dropoff"]:
                        self.higher_obstacle_bins[bin_index] += 1
                        self.higher_obstacles_bin_files[bin_index].append(
                            {"name": data["name"], "startFrame": obstacle["start_frame"]}
                        )

                    elif obstacle["is_dropoff"] and not obstacle["is_higher_obstacle"]:
                        self.dropoff_bins[bin_index] += 1
                        self.dropoff_bins_files[bin_index].append(
                            {"name": data["name"], "startFrame": obstacle["start_frame"]}
                        )
                    elif obstacle["is_dropoff"] and obstacle["is_higher_obstacle"]:
                        self._count_both_type += 1
                        self.dropoff_higher_obstacle.append(
                            {"name": data["name"], "startFrame": obstacle["start_frame"]}
                        )
                    else:
                        print(
                            f"[WARNING] Obstacle Detected but does not belong to any category, problem in code"
                        )

    def _write_evaluation(self):
        pass

    def _print_evaluation(self):
        pass

    def _create_output_folder(self):
        pass
