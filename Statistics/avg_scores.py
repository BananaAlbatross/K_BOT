import sqlite3
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

DB_PATH = "C:/Users/Kaare/Desktop/UT/Andmed/Turniir.db"
SAVE_FOLDER = "C:/Users/Kaare/Desktop/UT/Andmed"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT Player1, Player2, Score FROM tournament_results')
rows = cursor.fetchall()
conn.close()

scores = defaultdict(list)
for player1, player2, score in rows:
    scores[player1].append(score)
    scores[player2].append(100 - score)

bot_avgs = {bot: sum(s) / len(s) for bot, s in scores.items()}

# Group averages
eval_groups = ['A', 'B', 'C']
eval_labels = ['Grupp A', 'Grupp B', 'Grupp C']
eval_avgs = []
eval_fns = []
for group in eval_groups:
    group_scores = [s for bot in scores for s in scores[bot] if f'BOT_{group}' in bot]
    eval_avgs.append(sum(group_scores) / len(group_scores))
    eval_fns.append(lambda bot, g=group: f'BOT_{g}' in bot)

algo_groups = ['1', '2', '3', '4']
algo_labels = ['Grupp 1', 'Grupp 2', 'Grupp 3', 'Grupp 4']
algo_avgs = []
algo_fns = []
for num in algo_groups:
    group_scores = [s for bot in scores for s in scores[bot] if bot.endswith(num)]
    algo_avgs.append(sum(group_scores) / len(group_scores))
    algo_fns.append(lambda bot, n=num: bot.endswith(n))


def plot_column_chart(labels, avgs, bot_avgs, match_fns, title, filename, bar_color, bot_color):
    fig, ax = plt.subplots(figsize=(9, 6))

    x = np.arange(len(labels))
    bar_width = 0.5

    # Bars
    bars = ax.bar(x, avgs, width=bar_width, color=bar_color, zorder=2, label='Group average')

    # Bots
    for i, match_fn in enumerate(match_fns):
        matching = {bot: v for bot, v in bot_avgs.items() if match_fn(bot)}
        jitter = np.linspace(-0.15, 0.15, len(matching))
        for j, (bot, val) in enumerate(sorted(matching.items())):
            short = bot.replace('K_BOT_', '')
            ax.scatter(i + jitter[j], val, color=bot_color, zorder=3, s=60)
            ax.annotate(short, (i + jitter[j], val),
                        textcoords="offset points", xytext=(0, 6),
                        ha='center', fontsize=8, color=bot_color)

    # Bars
    for bar, val in zip(bars, avgs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                f'{val:.1f}'.replace(".", ","), ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel('Keskmine matšiskoor', fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_ylim(0, 80)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(f"{SAVE_FOLDER}/{filename}.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved {filename}.png")


plot_column_chart(
    eval_labels, eval_avgs, bot_avgs, eval_fns,
    title='Keskmine matšiskoor hindamisfunktsiooni järgi',
    filename='avg_by_eval',
    bar_color='turquoise',
    bot_color='teal'
)

plot_column_chart(
    algo_labels, algo_avgs, bot_avgs, algo_fns,
    title='Keskmine matšiskoor otsingualgoritmi järgi',
    filename='avg_by_search',
    bar_color='darkorchid',
    bot_color='indigo'
)
