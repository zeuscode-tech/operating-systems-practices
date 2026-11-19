"""Пошаговая трассировка FIFO и LRU: состояние кадров после каждого обращения."""
from collections import deque

CONTROL = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]


def trace_fifo(refs, n_frames):
    frames = []
    queue = deque()
    for step, page in enumerate(refs, 1):
        mark = "  "
        if page not in frames:
            mark = "PF"
            if len(frames) < n_frames:
                frames.append(page)
            else:
                victim = queue.popleft()
                frames[frames.index(victim)] = page
            queue.append(page)
        cells = " ".join(str(p) for p in frames)
        print(f"{step:>2}  обр={page}  [{cells:<5}]  {mark}")


def trace_lru(refs, n_frames):
    frames = []
    last_used = {}
    for step, page in enumerate(refs, 1):
        mark = "  "
        if page not in frames:
            mark = "PF"
            if len(frames) < n_frames:
                frames.append(page)
            else:
                victim = min(frames, key=lambda p: last_used[p])
                frames[frames.index(victim)] = page
        last_used[page] = step
        cells = " ".join(str(p) for p in frames)
        print(f"{step:>2}  обр={page}  [{cells:<5}]  {mark}")


if __name__ == "__main__":
    print("FIFO, 3 кадра")
    trace_fifo(CONTROL, 3)
    print("\nLRU, 3 кадра")
    trace_lru(CONTROL, 3)
