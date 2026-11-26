from pathlib import Path
import pandas as pd


def sample_new_ball_service_games(n, output_csv, input_csv=None, seed=None):
    root = Path(__file__).parent
    input_path = Path(input_csv) if input_csv else root / "new_ball_service_games.csv"

    df = pd.read_csv(input_path)

    if n > len(df):
        print(f"Warning: Requested sample size {n} exceeds available rows {len(df)}. Exporting all {len(df)} rows.")
        sample_df = df
    else:
        sample_df = df.sample(n=n, random_state=seed).reset_index(drop=True)

    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(out_path, index=False)

    print(f"Exported {len(sample_df)} rows to {out_path}")
    return sample_df

sample_new_ball_service_games(n=3000, output_csv="sampled_new_ball_service_games.csv")
