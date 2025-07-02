from rich import box
from rich.console import Console
from rich.table import Table

import numpy as np
import os
import json
import csv


class EvaluationResults:
    def __init__(self, num_bins: int, num_files: int, max_distance: float = 4.0):
        self._count_obstacle_free = 0
        self._count_both_type = 0
        self.higher_obstacle_bins = np.zeros(num_bins, dtype=np.int16)
        self.dropoff_bins = np.zeros(num_bins, dtype=np.int16)
        self.higher_obstacles_bin_files = {n: [] for n in range(num_bins)}
        self.dropoff_bins_files = {n: [] for n in range(num_bins)}
        self.dropoff_higher_obstacle = []
        self.obstacle_free_file_names = []
        self._num_bins = num_bins
        self._max_distance = max_distance
        self._num_files = num_files
        self.durations_of_each_recording = []

    def print(self):
        self.log_to_console()

    def _get_bin_ranges(self):
        bin_width = self._max_distance / self._num_bins
        return [
            (round(i * bin_width, 2), round((i + 1) * bin_width, 2)) for i in range(self._num_bins)
        ]

    def _rich_combined_obstacle_table(self, table_format: box.Box = box.HORIZONTALS) -> Table:
        bin_ranges = self._get_bin_ranges()
        table = Table(
            title="[bold blue]Obstacle Distribution by Distance Bin[/bold blue]",
            box=table_format,
            expand=True,
        )
        table.add_column(
            "Bin Range (m)", justify="center", header_style="bold magenta", style="cyan"
        )
        table.add_column(
            "Higher Obstacle Count", justify="center", header_style="bold green", style="green"
        )
        table.add_column(
            "Dropoff Count", justify="center", header_style="bold yellow", style="yellow"
        )
        for i, (start, end) in enumerate(bin_ranges):
            table.add_row(
                f"{start:.2f} - {end:.2f}",
                str(self.higher_obstacle_bins[i]),
                str(self.dropoff_bins[i]),
            )
        return table

    def _rich_all_obstacle_analysis(self, table_format: box.Box = box.HORIZONTALS) -> Table:
        total_higher = int(np.sum(self.higher_obstacle_bins))
        total_dropoff = int(np.sum(self.dropoff_bins))
        total_both = self._count_both_type
        total_obstacles = total_higher + total_dropoff + total_both
        table = Table(
            title="[bold red]Overall Obstacle Statistics[/bold red]",
            box=table_format,
            expand=True,
            title_style="bold red",
        )
        table.add_column("Type", justify="center", header_style="bold magenta", style="cyan")
        table.add_column("Count", justify="center", header_style="bold magenta", style="yellow")
        table.add_row("Total Obstacles", str(total_obstacles), style="bold")
        table.add_row("Higher Obstacles", str(total_higher), style="green")
        table.add_row("Dropoff Obstacles", str(total_dropoff), style="blue")
        table.add_row("Both (Higher & Dropoff)", str(total_both), style="magenta")
        return table

    def log_to_console(self, num_files: int = 0) -> None:
        if self._num_bins == 0:
            return
        console = Console()
        console.print(self._rich_combined_obstacle_table())
        console.print()
        console.print(self._rich_filenames_and_obstacle_frequency())
        console.print()
        console.print(self._rich_duration_of_each_file())
        console.print()
        console.print(self._rich_all_obstacle_analysis())

        n_free = len(self.obstacle_free_file_names)
        if self._num_files:
            msg = f"[bold green]{n_free} out of {self._num_files} files had no obstacles.[/bold green]"
        else:
            msg = f"[bold green]{n_free} files had no obstacles.[/bold green]"
        console.print("\n[bold underline]Obstacle-Free Files[/bold underline]\n")
        console.print(msg)

    def log_to_file(self, file_path: str) -> None:
        """
        Write the obstacle analysis results to a text file at the given file path.
        Includes bin counts for higher and dropoff obstacles, overall statistics, and obstacle-free file names.
        """
        bin_ranges = self._get_bin_ranges()
        with open(file_path, "w") as f:
            f.write("Obstacle Distribution by Distance Bin\n")
            f.write("=" * 40 + "\n")
            f.write(f"{'Bin Range (m)':<20}{'Higher Obstacle':<20}{'Dropoff':<20}\n")
            for i, (start, end) in enumerate(bin_ranges):
                f.write(
                    f"{start:.2f} - {end:.2f}    {self.higher_obstacle_bins[i]:<20}{self.dropoff_bins[i]:<20}\n"
                )
            f.write("\nOverall Obstacle Statistics\n")
            f.write("=" * 40 + "\n")
            total_higher = int(np.sum(self.higher_obstacle_bins))
            total_dropoff = int(np.sum(self.dropoff_bins))
            total_both = self._count_both_type
            total_obstacles = total_higher + total_dropoff + total_both
            f.write(f"Total Obstacles: {total_obstacles}\n")
            f.write(f"Higher Obstacles: {total_higher}\n")
            f.write(f"Dropoff Obstacles: {total_dropoff}\n")
            f.write(f"Both (Higher & Dropoff): {total_both}\n")
            n_free = len(self.obstacle_free_file_names)
            if self._num_files:
                msg = f"{n_free} out of {self._num_files} files had no obstacles."
            else:
                msg = f"{n_free} files had no obstacles."
            f.write("\nObstacle-Free Files\n")
            f.write("=" * 40 + "\n")
            f.write(msg + "\n")
            for name in self.obstacle_free_file_names:
                f.write(f"{name}\n")

        # Save obstacle frequency as JSON in the same folder
        csv_path = os.path.splitext(file_path)[0] + "_obstacle_frequency.csv"
        self.save_obstacle_frequency_csv(csv_path)

    def _rich_duration_of_each_file(self, table_format: box.Box = box.HORIZONTALS) -> Table:
        """
        Return a rich Table displaying the duration of each file in minutes.
        The durations are stored in durations_of_each_recording as dicts with 'name' and 'duration' (in seconds).
        """

        table = Table(
            title="[bold blue]Duration of Each File (in Minutes)[/bold blue]",
            box=table_format,
            expand=True,
        )
        table.add_column("File Name", justify="center", header_style="bold magenta", style="cyan")
        table.add_column(
            "Duration (minutes)", justify="center", header_style="bold green", style="green"
        )
        filenames = set()
        for entry in self.durations_of_each_recording:
            name = entry.get("name", "N/A")
            duration_sec = entry.get("duration", 0)

            if duration_sec == 0 or name == "N/A":
                continue
            if name in filenames:
                continue
            filenames.add(name)
            duration_min = round(duration_sec / 60, 2)
            table.add_row(str(name), f"{duration_min}")
        return table

    def _rich_filenames_and_obstacle_frequency(
        self, table_format: box.Box = box.HORIZONTALS
    ) -> Table:
        """
        Return a rich Table where each row is a file name and each column is a bin range (e.g., 0.0-0.5, 0.5-1.0, ...).
        Each cell displays 'higher_obstacle_frequency | dropoff_frequency' for that file and bin.
        The last column and last row show totals.
        """
        bin_ranges = self._get_bin_ranges()
        file_names = set()
        for bin_files in self.higher_obstacles_bin_files.values():
            for f in bin_files:
                file_names.add(f["name"])
        for bin_files in self.dropoff_bins_files.values():
            file_names.add(f["name"])

        file_names = sorted(file_names)
        table = Table(
            title="[bold blue]File-wise Obstacle Frequency by Bin[/bold blue]",
            box=table_format,
            expand=True,
        )
        table.add_column("File Name", justify="center", header_style="bold magenta", style="cyan")
        for start, end in bin_ranges:
            table.add_column(f"{start:.2f}-{end:.2f}", justify="center", style="white")
        table.add_column("Total", justify="center", header_style="bold yellow", style="yellow")

        # For each file, count how many times it appears in each bin for higher and dropoff
        file_totals = []
        for file_name in file_names:
            row = [file_name]
            has_obstacle = False
            file_higher_total = 0
            file_dropoff_total = 0
            for bin_idx in range(self._num_bins):
                higher_count = sum(
                    1
                    for f in self.higher_obstacles_bin_files[bin_idx]
                    if f.get("name") == file_name
                )
                dropoff_count = sum(
                    1 for f in self.dropoff_bins_files[bin_idx] if f.get("name") == file_name
                )
                if higher_count > 0 or dropoff_count > 0:
                    has_obstacle = True
                row.append(f"{higher_count} | {dropoff_count}")
                file_higher_total += higher_count
                file_dropoff_total += dropoff_count
            file_total = file_higher_total + file_dropoff_total
            row.append(f"{file_total}")
            file_totals.append(file_total)
            if has_obstacle:
                table.add_row(*row)

        # Add a total row at the end
        total_higher_per_bin = []
        total_dropoff_per_bin = []
        for bin_idx in range(self._num_bins):
            total_higher = sum(
                1 for f in self.higher_obstacles_bin_files[bin_idx] if f.get("name") in file_names
            )
            total_dropoff = sum(
                1 for f in self.dropoff_bins_files[bin_idx] if f.get("name") in file_names
            )
            total_higher_per_bin.append(total_higher)
            total_dropoff_per_bin.append(total_dropoff)

        total_row = ["[bold]Total[/bold]"]
        grand_total = 0
        for h, d in zip(total_higher_per_bin, total_dropoff_per_bin):
            total_row.append(f"[bold]{h} | {d}[/bold]")
            grand_total += h + d
        total_row.append(f"[bold]{grand_total}[/bold]")

        table.add_row()
        table.add_row(*total_row, style="bold")
        return table

    def save_obstacle_frequency_json(self, file_path: str):
        bin_ranges = self._get_bin_ranges()
        file_names = set()
        for bin_files in self.higher_obstacles_bin_files.values():
            for fdict in bin_files:
                file_names.add(fdict["name"])
        for bin_files in self.dropoff_bins_files.values():
            for fdict in bin_files:
                file_names.add(fdict["name"])
        file_names = sorted(file_names)

        data = {}
        for file_name in file_names:
            bins = []
            file_higher_total = 0
            file_dropoff_total = 0
            for bin_idx, (start, end) in enumerate(bin_ranges):
                higher_count = sum(
                    1
                    for fdict in self.higher_obstacles_bin_files[bin_idx]
                    if fdict.get("name") == file_name
                )
                dropoff_count = sum(
                    1
                    for fdict in self.dropoff_bins_files[bin_idx]
                    if fdict.get("name") == file_name
                )
                bins.append(
                    {
                        "range": f"{start:.2f}-{end:.2f}",
                        "higher": higher_count,
                        "dropoff": dropoff_count,
                    }
                )
                file_higher_total += higher_count
                file_dropoff_total += dropoff_count
            file_total = file_higher_total + file_dropoff_total
            data[file_name] = {"bins": bins, "total": file_total}

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def save_obstacle_frequency_csv(self, file_path: str):
        bin_ranges = self._get_bin_ranges()
        file_names = set()
        for bin_files in self.higher_obstacles_bin_files.values():
            for fdict in bin_files:
                file_names.add(fdict["name"])
        for bin_files in self.dropoff_bins_files.values():
            for fdict in bin_files:
                file_names.add(fdict["name"])
        file_names = sorted(file_names)

        # Prepare header: File Name, each bin, Total Higher, Total Dropoff, Grand Total
        header = (
            ["File Name"]
            + [f"{start:.2f}-{end:.2f}" for (start, end) in bin_ranges]
            + ["Total Higher", "Total Dropoff", "Grand Total"]
        )

        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            for file_name in file_names:
                row = [file_name]
                file_higher_total = 0
                file_dropoff_total = 0
                for bin_idx, (start, end) in enumerate(bin_ranges):
                    higher_count = sum(
                        1
                        for fdict in self.higher_obstacles_bin_files[bin_idx]
                        if fdict.get("name") == file_name
                    )
                    dropoff_count = sum(
                        1
                        for fdict in self.dropoff_bins_files[bin_idx]
                        if fdict.get("name") == file_name
                    )
                    row.append(f"{higher_count}|{dropoff_count}")
                    file_higher_total += higher_count
                    file_dropoff_total += dropoff_count
                grand_total = file_higher_total + file_dropoff_total
                row.extend([str(file_higher_total), str(file_dropoff_total), str(grand_total)])
                writer.writerow(row)
