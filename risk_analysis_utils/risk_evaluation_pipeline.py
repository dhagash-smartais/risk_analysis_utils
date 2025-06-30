import os
import tqdm
import json
from risk_analysis_utils.tools.evaluation_results import EvaluationResults


class RiskEvaluationPipeline:
    def __init__(self, evaluation_dir, max_distance=4.0, resolution=0.5):
        self.evaluation_dir = evaluation_dir
        self._n_videos = len([f for f in os.listdir(evaluation_dir) if f.endswith(".json")])

        self._resolution = resolution
        self._num_bins = int(max_distance / resolution)
        self.results = EvaluationResults(
            num_bins=self._num_bins, num_files=self._n_videos, max_distance=max_distance
        )

        self.results_dir = None

    def run(self):
        self._run_evaluation()
        return self.results

    def _run_evaluation(self):
        json_files = [file for file in os.listdir(self.evaluation_dir) if file.endswith(".json")]
        for file in tqdm.tqdm(json_files, desc="Processing JSON files"):
            file_path = os.path.join(self.evaluation_dir, file)
            with open(file_path, "r") as f:
                data = json.load(f)

                if not data["obstacles"]:
                    self.results._count_obstacle_free += 1
                    self.results.obstacle_free_file_names.append(data["name"])
                    continue

                for obstacle in data["obstacles"]:
                    distance = obstacle["distance"]
                    bin_index = int(distance // self._resolution)
                    if bin_index >= self._num_bins:
                        bin_index = self._num_bins - 1
                    if obstacle["is_higher_obstacle"] and not obstacle["is_dropoff"]:
                        self.results.higher_obstacle_bins[bin_index] += 1
                        self.results.higher_obstacles_bin_files[bin_index].append(
                            {"name": data["name"], "startFrame": obstacle["start_frame"]}
                        )

                    elif obstacle["is_dropoff"] and not obstacle["is_higher_obstacle"]:
                        self.results.dropoff_bins[bin_index] += 1
                        self.results.dropoff_bins_files[bin_index].append(
                            {"name": data["name"], "startFrame": obstacle["start_frame"]}
                        )
                    elif obstacle["is_dropoff"] and obstacle["is_higher_obstacle"]:
                        self.results._count_both_type += 1
                        self.results.dropoff_higher_obstacle.append(
                            {"name": data["name"], "startFrame": obstacle["start_frame"]}
                        )
                    else:
                        print(
                            f"[WARNING] Obstacle Detected but does not belong to any category, problem in code"
                        )

    def _write_evaluation(self):
        pass

    def _create_output_folder(self):
        pass
