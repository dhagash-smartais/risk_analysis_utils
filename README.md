# risk_analysis_utils

A utility package for analyzing risk and obstacle data from integration test results. It provides a command-line tool to process JSON files containing obstacle information and outputs detailed statistics and summaries.

## Installation

You can install the package using pip:

```bash
pip install .
```

or, if you are using a local clone:

```bash
pip install -e .
```

## Usage

After installation, use the provided CLI command to analyze your data:

```bash
risk_analysis_pipeline  <path_to_json_files> [--max-distance <float>] [--resolution <float>]
```

- `<path_to_json_files>`: Path to the directory containing your JSON files from the integration testing framework.
- `--max-distance`: (Optional) Maximum distance for evaluation (default: 4.0).
- `--resolution`: (Optional) Resolution of each bin (default: 0.5).


This will print a summary of obstacle analysis to the console and save detailed results in the output directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Maintainer

Dhagash Desai - SmartAIs GmbH