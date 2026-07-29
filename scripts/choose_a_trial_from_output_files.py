import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def select_representative_trial(input_csv: Path, output_dir: Path) -> None:
    """Select the trial closest to the median transformer configuration."""

    df = pd.read_csv(input_csv)

    required_columns = {
        "trial",
        "cluster_index",
        "chosen_transformer_kva",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Create one summary row per trial.
    summary = (
        df.groupby("trial")
        .agg(
            n_transformers=("cluster_index", "count"),
            installed_kva=("chosen_transformer_kva", "sum"),
            n_25kva=("chosen_transformer_kva", lambda x: (x == 25).sum()),
            n_50kva=("chosen_transformer_kva", lambda x: (x == 50).sum()),
            n_75kva=("chosen_transformer_kva", lambda x: (x == 75).sum()),
            n_oversize=("chosen_transformer_kva", lambda x: x.isna().sum()),
        )
        .reset_index()
    )

    comparison_columns = [
        "n_transformers",
        "installed_kva",
        "n_25kva",
        "n_50kva",
        "n_75kva",
        "n_oversize",
    ]

    medians = summary[comparison_columns].median()

    # Normalize each difference so installed_kva does not dominate the score.
    scale = medians.abs().replace(0, 1)

    summary["distance_to_median"] = np.sqrt(
        (
            (summary[comparison_columns] - medians)
            .div(scale)
            .pow(2)
            .sum(axis=1)
        )
    )

    representative_trial = int(
        summary.loc[summary["distance_to_median"].idxmin(), "trial"]
    )

    selected_assignments = df[df["trial"] == representative_trial].copy()

    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "method4_trial_summary.csv"
    selected_path = output_dir / "method4_representative_trial.csv"

    summary.sort_values("distance_to_median").to_csv(summary_path, index=False)
    selected_assignments.to_csv(selected_path, index=False)

    selected_summary = summary[summary["trial"] == representative_trial].iloc[0]

    print(f"Representative trial: {representative_trial}")
    print(f"Number of transformers: {int(selected_summary['n_transformers'])}")
    print(f"Installed capacity: {selected_summary['installed_kva']:.1f} kVA")
    print(f"25 kVA transformers: {int(selected_summary['n_25kva'])}")
    print(f"50 kVA transformers: {int(selected_summary['n_50kva'])}")
    print(f"75 kVA transformers: {int(selected_summary['n_75kva'])}")
    print(f"Oversized clusters: {int(selected_summary['n_oversize'])}")
    print(f"\nSaved summary to: {summary_path}")
    print(f"Saved selected assignments to: {selected_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Choose the Method 4 trial closest to the median configuration."
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Path to the Method 4 cluster assignments CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory for the output CSV files.",
    )

    args = parser.parse_args()
    select_representative_trial(args.input_csv, args.output_dir)


if __name__ == "__main__":
    main()
