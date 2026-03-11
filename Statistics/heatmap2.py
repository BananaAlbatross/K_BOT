import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from copy import copy

A4_also = False
save_folder = "C:/Users/Kaare/Desktop/UT/Andmed"  # <-- change this

df = pd.read_csv("C:/Users/Kaare/Desktop/UT/Andmed/tournament_results.csv")
    
if not A4_also:
    df = df[df["Player1"].str.contains("A[123]|B[123]|C[123]", regex=True) &
        df["Player2"].str.contains("A[123]|B[123]|C[123]", regex=True)]
    
bots = sorted(set(df["Player1"]).union(set(df["Player2"])))

W        = pd.DataFrame(np.nan, index=bots, columns=bots)
D        = pd.DataFrame(np.nan, index=bots, columns=bots)
L        = pd.DataFrame(np.nan, index=bots, columns=bots)
WL_delta = pd.DataFrame(np.nan, index=bots, columns=bots)
Score    = pd.DataFrame(np.nan, index=bots, columns=bots)

for _, row in df.iterrows():
    p1, p2 = row["Player1"], row["Player2"]
    w, d, l = row["W"], row["D"], row["L"]
    score = row["Score"]

    W.loc[p1, p2]        = w
    D.loc[p1, p2]        = d
    L.loc[p1, p2]        = l
    WL_delta.loc[p1, p2] = w - l
    Score.loc[p1, p2]    = score

    W.loc[p2, p1]        = l
    D.loc[p2, p1]        = d
    L.loc[p2, p1]        = w
    WL_delta.loc[p2, p1] = l - w
    Score.loc[p2, p1]    = 100 - score

def plot_heatmap(matrix, title, cmap_name, filename):
    cmap = copy(plt.cm.get_cmap(cmap_name))
    cmap.set_bad(color="#dddddd")

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(np.ma.masked_invalid(matrix.values), cmap=cmap, aspect="equal")

    short = [b.replace("K_BOT_", "") for b in bots]
    ax.set_xticks(range(len(bots)))
    ax.set_yticks(range(len(bots)))
    ax.set_xticklabels(short, rotation=90)
    ax.set_yticklabels(short)
    ax.set_title(title, fontsize=14, fontweight="bold")

    for i in range(len(bots)):
        for j in range(len(bots)):
            val = matrix.iloc[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.0f}",
                        ha="center", va="center", fontsize=7)

    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(f"{save_folder}/{filename}.png", dpi=150, bbox_inches="tight")
    plt.close()

plot_heatmap(W,        "Võitude arv",              "Greens",  "1_voidud")
plot_heatmap(D,        "Viikide arv",              "Blues",   "2_viigid")
plot_heatmap(L,        "Kaotuste arv",             "Reds",    "3_kaotused")
plot_heatmap(WL_delta, "Võitude ja kaotuste vahe", "RdYlGn",  "4_wl_delta")
plot_heatmap(Score,    "Matši skoor",              "YlOrRd",  "5_skoor")