from rich import box
from rich.console import Console
from rich.table import Table

import numpy as np


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

    def _rich_all_obstacle_analysis(self, table_format: box.Box = box.SIMPLE_HEAVY) -> Table:
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
