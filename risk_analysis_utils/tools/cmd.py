import typer
from pathlib import Path

app = typer.Typer(add_completion=False, rich_markup_mode="rich")


@app.command(help="Get the analysis of the obstacles from integration testing framework")
def get_evaluation_results(
    data: Path = typer.Argument(..., help="Path to all the json files", show_default=False),
    max_distance: float = typer.Option(
        4.0, help="Maximum distance for evaluation", rich_help_panel="Additional Options"
    ),
    resolution: float = typer.Option(
        0.5, help="Resolution of each bin", rich_help_panel="Additional Options"
    ),
):
    from risk_analysis_utils.risk_evaluation_pipeline import RiskEvaluationPipeline

    RiskEvaluationPipeline(
        evaluation_dir=data, max_distance=max_distance, resolution=resolution
    ).run().print()


def run():
    app()
