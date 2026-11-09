import os
import csv

def write_csv(path, all_game_stats):
    if not all_game_stats: return

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok = True)

    with open(path, "w", newline = "") as file:
        writer = csv.DictWriter(file, fieldnames = list(all_game_stats[0].keys()))
        writer.writeheader()
        writer.writerows(all_game_stats)