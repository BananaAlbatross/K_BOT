import sqlite3
from collections import defaultdict

conn = sqlite3.connect('C:/Users/Kaare/Desktop/UT/Andmed/Turniir.db')
cursor = conn.cursor()
cursor.execute('SELECT Player1, Player2, Score FROM tournament_results')
rows = cursor.fetchall()
conn.close()

scores = defaultdict(list)

for player1, player2, score in rows:
    scores[player1].append(score)
    scores[player2].append(100 - score)  # Score is from Player1's perspective

print(f"{'Bot':<15} {'Avg Score':>10} {'Matches':>10}")
print("-" * 37)
for bot in sorted(scores.keys()):
    avg = sum(scores[bot]) / len(scores[bot])
    print(f"{bot:<15} {avg:>10.2f} {len(scores[bot]):>10}")

# Group by eval (A, B, C)
print("\nBy eval function:")
print(f"{'Group':<10} {'Avg Score':>10}")
print("-" * 22)
for group in ['A', 'B', 'C']:
    group_scores = [s for bot in scores for s in scores[bot] if f'BOT_{group}' in bot]
    print(f"{group:<10} {sum(group_scores)/len(group_scores):>10.2f}")

# Group by algorithm (1, 2, 3, 4)
print("\nBy algorithm:")
print(f"{'Group':<10} {'Avg Score':>10}")
print("-" * 22)
for num in ['1', '2', '3', '4']:
    group_scores = [s for bot in scores for s in scores[bot] if bot.endswith(num)]
    print(f"{num:<10} {sum(group_scores)/len(group_scores):>10.2f}")