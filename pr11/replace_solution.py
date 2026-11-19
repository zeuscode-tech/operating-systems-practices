"""ПР-11. Алгоритмы замещения страниц: FIFO, LRU, Optimal, Clock.
Эталонное решение (уровни A и B)."""
import random
import sys
from collections import deque

CONTROL = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def fifo(refs, n_frames):
    frames = []
    queue = deque()
    faults = 0
    for page in refs:
        if page in frames:
            continue
        faults += 1
        if len(frames) < n_frames:
            frames.append(page)
        else:
            victim = queue.popleft()
            frames[frames.index(victim)] = page
        queue.append(page)
    return faults


def lru(refs, n_frames):
    frames = []
    last_used = {}
    faults = 0
    for t, page in enumerate(refs):
        if page not in frames:
            faults += 1
            if len(frames) < n_frames:
                frames.append(page)
            else:
                victim = min(frames, key=lambda p: last_used[p])
                frames[frames.index(victim)] = page
        last_used[page] = t
    return faults


def optimal(refs, n_frames):
    frames = []
    faults = 0
    for i, page in enumerate(refs):
        if page in frames:
            continue
        faults += 1
        if len(frames) < n_frames:
            frames.append(page)
            continue
        future = refs[i + 1:]

        def next_use(p):
            return future.index(p) if p in future else len(future) + 1

        victim = max(frames, key=next_use)
        frames[frames.index(victim)] = page
    return faults


def clock(refs, n_frames):
    frames = [None] * n_frames
    ref_bit = [0] * n_frames
    hand = 0
    faults = 0
    for page in refs:
        if page in frames:
            ref_bit[frames.index(page)] = 1
            continue
        faults += 1
        while ref_bit[hand] == 1:
            ref_bit[hand] = 0
            hand = (hand + 1) % n_frames
        frames[hand] = page
        ref_bit[hand] = 1
        hand = (hand + 1) % n_frames
    return faults


ALGOS = {"FIFO": fifo, "LRU": lru, "Optimal": optimal, "Clock": clock}


def table(refs, frame_range):
    print("кадры | " + " | ".join(f"{name:>7}" for name in ALGOS))
    rows = {}
    for n in frame_range:
        row = [ALGOS[name](refs, n) for name in ALGOS]
        rows[n] = row
        print(f"{n:>5} | " + " | ".join(f"{v:>7}" for v in row))
    return rows


def locality_refs(length, n_pages, seed):
    rng = random.Random(seed)
    refs = []
    base = 0
    for _ in range(length):
        if rng.random() < 0.1:
            base = rng.randrange(n_pages)
        refs.append((base + rng.randrange(3)) % n_pages)
    return refs


def random_refs(length, n_pages, seed):
    rng = random.Random(seed)
    return [rng.randrange(n_pages) for _ in range(length)]


def main():
    print("== Контрольная строка, 3 кадра ==")
    for name, fn in ALGOS.items():
        print(f"{name:>7}: {fn(CONTROL, 3)} отказов")

    print("\n== Контрольная строка, 1..8 кадров ==")
    rows = table(CONTROL, range(1, 9))

    print("\n== Аномалия Белади (строка 1 2 3 4 1 2 5 1 2 3 4 5) ==")
    table(BELADY, range(3, 5))

    print("\n== Локальность против случайности (1000 обращений, 20 страниц, 5 кадров) ==")
    loc = locality_refs(1000, 20, seed=42)
    rnd = random_refs(1000, 20, seed=42)
    print("строка      | " + " | ".join(f"{name:>7}" for name in ALGOS))
    for label, refs in (("локальная", loc), ("случайная", rnd)):
        print(f"{label:<11} | " + " | ".join(f"{ALGOS[n](refs, 5):>7}" for n in ALGOS))

    if "--plot" in sys.argv:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xs = list(rows)
        for i, name in enumerate(ALGOS):
            plt.plot(xs, [rows[n][i] for n in xs], marker="o", label=name)
        plt.xlabel("Число кадров")
        plt.ylabel("Число страничных отказов")
        plt.title("Контрольная строка: кадры -> отказы")
        plt.grid(alpha=0.3)
        plt.legend()
        plt.savefig("faults_vs_frames.png", dpi=150, bbox_inches="tight")
        print("\nграфик сохранён: faults_vs_frames.png")


if __name__ == "__main__":
    main()
