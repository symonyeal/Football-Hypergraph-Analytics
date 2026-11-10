"""Feature blocks of a possession at the cutoff (docs/HYPOTHESES.md H4). Block 2 (VAEP) comes from socceraction in run.py.

Legend: first the on-ball actions up to the cutoff, ctx context at the possession start, P players so far.
"""


from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import MaxAbsScaler


def design(Dtr, Dte):
    """Sparse matrices from feature dicts. Max-abs scaling leaves 0/1 indicators unchanged; standardizing them would
    multiply a rare indicator by 1/sd and defeat the L2 penalty."""
    dv = DictVectorizer()
    Xtr = dv.fit_transform(Dtr)
    sc = MaxAbsScaler().fit(Xtr)
    return sc.transform(Xtr), sc.transform(dv.transform(Dte)), list(dv.feature_names_)


def zone(l):
    """Cell of a 6 x 4 grid on the 120 x 80 pitch."""
    return f"z{min(int(l[0] // 20), 5)}_{min(int(l[1] // 20), 3)}"


def motif(first):
    """Actor pattern of the actions: ABB = one player, then a second player twice."""
    s = {}
    return "".join(s.setdefault(e["player"]["id"], "ABCDEFG"[len(s)]) for e in first)


def features(first, ctx, P):
    """Sparse indicator blocks 0 (context), 1 (players, ordered pass pairs), 3 (motif), 5 (player set)."""
    b0 = {zone(first[0]["location"]): 1, f"pp={ctx['pattern']}": 1, f"diff={max(-2, min(2, ctx['diff']))}": 1,
          f"min={min(ctx['minute'] // 15, 6)}": 1}
    if ctx["home"]:
        b0["home"] = 1
    b1 = {f"p={v}": 1 for v in sorted(P)}
    for e in first:
        r = e.get("pass", {}).get("recipient")
        if r:
            b1[f"{e['player']['id']}>{r['id']}"] = 1
    return {0: b0, 1: b1, 3: {f"motif={motif(first)}": 1}, 5: {"set=" + ",".join(map(str, sorted(P))): 1}}
