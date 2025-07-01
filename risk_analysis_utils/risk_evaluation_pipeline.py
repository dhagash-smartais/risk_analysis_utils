import os
import tqdm
import json
import datetime
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
        self._create_output_folder()
        self._write_evaluation()
        self._write_results_to_file()
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
                    # [TODO: Dhagash] Should we keep this check?
                    if (obstacle["end_frame"] - obstacle["start_frame"]) < 3:
                        continue
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

    def _write_results_to_file(self):
        if self.results_dir is None:
            raise ValueError(
                "results_dir is not set. Please ensure the output folder is created before writing evaluation."
            )
        filename = "evaluation_results.txt"
        filepath = os.path.join(str(self.results_dir), filename)
        self.results.log_to_file(filepath)

    def _write_evaluation(self):
        if self.results_dir is None:
            raise ValueError(
                "results_dir is not set. Please ensure the output folder is created before writing evaluation."
            )
        filename = "file_names_with_obstatce_ranges.txt"
        filepath = os.path.join(str(self.results_dir), filename)
        with open(filepath, "w") as f:
            for i in range(self._num_bins):
                range_start = i * self._resolution
                range_end = (i + 1) * self._resolution
                filenames = [entry["name"] for entry in self.results.higher_obstacles_bin_files[i]]
                if filenames:
                    f.write(f"Obstacles in range {range_start:.1f} to {range_end:.1f}m:\n")
                    for name in filenames:
                        f.write(f"    - {name}\n")
                    f.write("\n")

    @staticmethod
    def _get_results_dir(evaluation_dir: str):
        results_dir = os.path.join(
            evaluation_dir, "results", datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        )
        latest_dir = os.path.join(
            os.path.realpath(os.path.join(evaluation_dir, "results")), "latest"
        )
        os.makedirs(results_dir, exist_ok=True)
        os.unlink(latest_dir) if os.path.exists(latest_dir) or os.path.islink(latest_dir) else None
        os.symlink(results_dir, latest_dir)

        return results_dir

    def _create_output_folder(self):
        self.results_dir = self._get_results_dir(self.evaluation_dir)
