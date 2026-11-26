from pathlib import Path
import pandas as pd

NEW_BALL_START_GAME = 8
NEW_BALL_INTERVAL = 9

def _parse_game_tokens(pbp_raw):
    # Parse pbp sequence into individual game tokens, excluding set separators.
    pbp_string = str(pbp_raw or "").strip()
    if not pbp_string:
        return []

    games = []
    for set_part in pbp_string.split("."):
        set_part = set_part.strip()
        if not set_part:
            continue
        # split games in set by semicolon, ignore empty
        for game in set_part.split(";"):
            g = game.strip()
            if g:
                games.append(g)
    return games


def _game_stats(pbp_game):
    # Return server stats for a single game string from pbp.
    game = str(pbp_game).strip().upper()
    points_list = list(game)

    total_points = len(points_list)
    server_points = sum(1 for p in points_list if p in {"S", "A"})
    ace_count = points_list.count("A")
    double_fault_count = points_list.count("D")

    last = points_list[-1] if total_points > 0 else None
    if last in {"R", "D"}:
        game_won = False
    elif last in {"S", "A"}:
        game_won = True
    else:
        game_won = None

    return {
        "point_win_rate": server_points / total_points if total_points > 0 else 0.0,
        "ace_count": ace_count,
        "double_fault_count": double_fault_count,
        "points_played": total_points,
        "game_won": game_won,
    }


def _is_tiebreak(game):
    return "/" in str(game)


def _new_ball_game_indices(game_tokens):
    # Return 0-based indices for new-ball service games with tiebreak push-forward.
    game_count = len(game_tokens)
    indices = []
    current_change_game = NEW_BALL_START_GAME  # 1-based intended game for ball change

    while current_change_game <= game_count:
        candidate_idx = current_change_game - 1

        # if change lands on tiebreak, push to next non-tiebreak game
        shift_idx = candidate_idx
        while shift_idx < game_count and _is_tiebreak(game_tokens[shift_idx]):
            shift_idx += 1

        if shift_idx >= game_count:
            break

        indices.append(shift_idx)

        # next change occurs after NEW_BALL_INTERVAL games after this actual change
        current_change_game = shift_idx + 1 + NEW_BALL_INTERVAL

    return indices

def extract_new_ball_service_games_from_match(match_row):
    # Extract rows for each new-ball service game from one match row.
    pbp_raw = match_row.get("pbp", "")
    game_tokens = _parse_game_tokens(pbp_raw)
    if not game_tokens:
        return []

    indices = _new_ball_game_indices(game_tokens)
    rows = []

    server1 = match_row.get("server1", "")
    server2 = match_row.get("server2", "")

    for game_idx in indices:
        if game_idx >= len(game_tokens):
            break

        game = game_tokens[game_idx]
        server = server1 if game_idx % 2 == 0 else server2

        stats = _game_stats(game)

        if _is_tiebreak(game):
            continue

        rows.append(
            {
                "pbp_id": match_row.get("pbp_id"),
                "date": match_row.get("date"),
                "tny_name": match_row.get("tny_name"),
                "server": server,
                "game_number": game_idx + 1,
                "points_played": stats["points_played"],
                "point_win_rate": stats["point_win_rate"],
                "ace_count": stats["ace_count"],
                "double_fault_count": stats["double_fault_count"],
                "game_won": stats["game_won"],
            }
        )

    return rows


def sample_and_export_new_ball_service_games(output_csv,data_root=None):
    root = Path(data_root) if data_root else Path(__file__).parent / "data"

    input_files = ["pbp_matches_atp_main_current.csv", "pbp_matches_atp_main_archive.csv"]

    extracted_rows = []

    for filename in input_files:
        path = root / filename

        df = pd.read_csv(path)

        for _, row in df.iterrows():
            extracted_rows.extend(extract_new_ball_service_games_from_match(row))

    if not extracted_rows:
        print("No new-ball service-game rows were generated.")
        result_df = pd.DataFrame(
            columns=[
                "pbp_id",
                "date",
                "tny_name",
                "server",
                "game_number",
                "points_played",
                "point_win_rate",
                "ace_count",
                "double_fault_count",
                "game_won",
            ]
        )
    else:
        result_df = pd.DataFrame(extracted_rows)

    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(out_path, index=False)

    print(f"Exported {len(result_df)} new-ball service-game rows to {out_path}")
    return result_df

sample_and_export_new_ball_service_games(output_csv="new_ball_service_games.csv")
