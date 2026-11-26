# Do New Tennis Balls Improve a Server’s Chances?

An exploratory statistics project examining whether servers win a larger proportion of points and service games immediately after a tennis ball change.

**Authors:** Matthew Yoon and Henry Liao  
**Context:** Advanced Statistics final project

## Research question

Tennis commentators often mention that a player is “serving with new balls.” We wanted to investigate whether that observation corresponds to a measurable advantage.

Using historical ATP point-by-point data attributed in our report to Jeff Sackmann, we built a Python pipeline to extract service-game statistics, classify games by their position in the ball-change cycle, and randomly sample games for a comparison of proportions.

## Main results

The original report used samples of **3,000 service games per group**:

| Outcome | New-ball group | Comparison group | Difference | One-sided p-value |
| --- | --- | --- | --- | --- |
| Points won by the server | 11,732 / 18,258 (64.26%) | 11,665 / 18,425 (63.31%) | +0.95 percentage points | 0.0297 |
| Service games won by the server | 2,386 / 3,000 (79.53%) | 2,355 / 3,000 (78.50%) | +1.03 percentage points | 0.1628 |

Under the original two-proportion z-test assumptions, the point-level comparison met the 0.05 significance threshold, while the game-level comparison did not. The observed differences were small, and these observational data do not establish that new balls caused better outcomes.

The point-level result requires particular caution: we sampled complete service games, so points within games may be correlated. The original calculation treats points as independent and does not adjust for clustering within games, matches, or players.

These values reproduce the calculations from the aggregate counts in the report. The original input data and sampled CSVs were not supplied with the source scripts, so the full extraction and sampling pipeline has not been independently reproduced here.

## Group definitions

The scripts infer ball changes from game order rather than an explicit ball-change field:

- **New-ball group:** The first service game following an inferred ball change. The code starts at game 8, then advances by 9 games after each actual inferred change.
- **Comparison / “old-ball” group:** Every other non-tiebreak game, including games at different stages of ball wear and the opening games of a match.
- **Tiebreak handling:** A scheduled change that lands on a tiebreak token is moved to the next non-tiebreak game. Tiebreak games are excluded from both groups.

These are the implementation’s classification rules, not direct observations of ball condition. In particular, the comparison group does not mean “only the most worn balls.”

## Data-processing pipeline

1. Read the current and archived ATP main-draw point-by-point CSVs.
2. Split the `pbp` strings into game tokens using set and game separators.
3. Identify inferred new-ball games and comparison games.
4. Summarize each game: total points, server point-win rate, aces, double faults, and whether the server won the game.
5. Export a CSV for each group.
6. Randomly sample up to 3,000 games from each group, without replacement.
7. Use the resulting samples for the statistical comparisons described in the report.

The parser counts `S` and `A` as server-won points, `A` as an ace, and `D` as a double fault. It identifies a game’s winner from the final point token. Each character in a non-tiebreak game token contributes to its point count, so valid source encoding is important.

## Project files

| File | Purpose |
| --- | --- |
| `new_ball.py` | Extract inferred new-ball service games and export `new_ball_service_games.csv` |
| `old_ball.py` | Extract the remaining non-tiebreak games and export `old_ball_service_games.csv` |
| `sample_new_ball.py` | Sample games from the new-ball export |
| `sample_old_ball.py` | Sample games from the comparison export |
| `tally_service_games.py` | Count games and points in the full group exports |
| `Statistics Final Project.pdf` | Original written report, including hypothesis tests, confidence interval, visualizations, and discussion |

The supplied Python files perform extraction, sampling, and tallying. They do not calculate the hypothesis tests, confidence interval, or report charts.

## Setup and usage

Use Python 3 and install pandas:

```bash
python -m pip install pandas
```

The dependency is identified from the source imports; exact versions from the original working environment are not recorded.

### 1. Supply the source data

Create a `data` folder beside the scripts and add:

- `data/pbp_matches_atp_main_current.csv`
- `data/pbp_matches_atp_main_archive.csv`

The code reads `pbp`, `server1`, `server2`, `pbp_id`, `date`, and `tny_name` from the match rows. Supply source files with the expected point-by-point encoding and metadata.

The original report describes historical coverage in 2011–2015 and partial 2017. The scripts do not independently enforce those dates or tournament-level restrictions. Preserve and document the exact source-data snapshot used when reproducing the project; filenames containing `current` do not identify a fixed version.

Add the exact upstream dataset link, snapshot information, and applicable attribution or redistribution terms before publishing data. The scripts do not download the datasets.

### 2. Extract the game groups

Run from the project folder:

```bash
python new_ball.py
python old_ball.py
```

Both exports are written to the current working directory.

### 3. Generate samples

```bash
python sample_new_ball.py
python sample_old_ball.py
```

Outputs:

- `sampled_new_ball_service_games.csv`
- `sampled_old_ball_service_games.csv`

Both scripts request 3,000 rows and export all available rows if fewer are present. Their default input paths are relative to the scripts, so running from the project folder keeps input and output paths aligned.

**Reproducibility:** The supplied calls do not set a random seed, so repeated runs can produce different samples and results. Both sampling functions accept a `seed` parameter. Set a fixed value, such as `seed=42`, in each bottom-of-file call for repeatable future runs. A new fixed seed will not reconstruct the original report’s samples.

### 4. Optional: tally full-dataset totals

`tally_service_games.py` currently looks for the two group exports inside `data/`, while the extraction scripts write them to the working directory. Either copy the full exports into `data/` or change these two assignments to match the extraction outputs:

```python
new_ball_file = "new_ball_service_games.csv"
old_ball_file = "old_ball_service_games.csv"
```

Then run:

```bash
python tally_service_games.py
```

This script summarizes the full extracted groups, not the sampled groups.

## Statistical approach

For both outcomes, the report tested:

- **Null hypothesis:** The population proportions are equal.
- **Alternative hypothesis:** The new-ball population proportion is greater than the comparison proportion.

The report used a one-sided, pooled two-proportion z-test at a significance level of 0.05. For points, it also calculated a two-sided 95% confidence interval for the difference:

**−0.038 to +1.930 percentage points.**

That interval includes zero even though the one-sided test has p < 0.05. These results use different rejection thresholds: a two-sided 95% interval corresponds to a two-sided test at 0.05, rather than the one-sided test used here. Both calculations retain the original independence assumptions.

The game-level p-value is approximately **0.163 > 0.05**. The original PDF has an inequality typo on the calculation line; its decision to fail to reject the null is consistent with the numerical p-value.

## Limitations

- **Dependence:** Sampling the groups separately does not guarantee independent point outcomes. Games can share matches and players, and points within games share conditions. A sampling-fraction check does not remove that dependence.
- **Observational comparison:** Player ability, opponent, surface, tournament, weather, and match situation can affect results. The analysis does not adjust for these factors.
- **Inferred labels:** Ball-change timing is reconstructed from game tokens. Match-opening games and special cases need validation against recorded ball changes.
- **Server attribution:** The code assigns servers by alternating game index. Service order after tiebreaks needs validation before relying on player-level metadata.
- **Input validation:** Missing point-by-point strings, unexpected token characters, overlapping source files, and incomplete games need explicit checks.
- **Historical coverage:** Findings describe the sampled historical data and should not automatically be generalized to current matches or other competition levels.
- **Reproducibility:** Original sampled CSVs, a fixed input snapshot, and executable statistical-analysis code are needed to reproduce the complete report.

## Contributions and future work

The report credits Henry with writing the Python sampling programs and discloses AI assistance with the logic for identifying ball-change game indices. Matthew and Henry are coauthors of the statistical report.

Future work could validate the parser against manually checked matches, compare first-after-change games with games immediately before a change, stratify by surface, and use an analysis that accounts for clustering within games, matches, and players.
