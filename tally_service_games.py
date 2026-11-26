import pandas as pd

new_ball_file = "data/new_ball_service_games.csv"
old_ball_file = "data/old_ball_service_games.csv"

new_ball_df = pd.read_csv(new_ball_file)
old_ball_df = pd.read_csv(old_ball_file)

new_ball_total_games = len(new_ball_df)
new_ball_total_points = new_ball_df["points_played"].sum()
old_ball_total_games = len(old_ball_df)
old_ball_total_points = old_ball_df["points_played"].sum()

print("NEW BALL:")
print(f"  Total Games: {new_ball_total_games}")
print(f"  Total Points Played: {new_ball_total_points}")

print("OLD BALL:")
print(f"  Total Games: {old_ball_total_games}")
print(f"  Total Points Played: {old_ball_total_points}")