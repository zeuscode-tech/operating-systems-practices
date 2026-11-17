"""ПР-11. Алгоритмы замещения страниц. Шаблон (уровень A).
FIFO уже реализован. Заполните lru и optimal (места помечены TODO)."""
from collections import deque

CONTROL = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]


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
                # TODO: выбрать жертву - страницу с наименьшим last_used
                victim = None
                frames[frames.index(victim)] = page
        # TODO: обновить last_used[page] (при КАЖДОМ обращении, не только при отказе)
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
        # TODO: для каждой страницы в frames найти, когда она понадобится в future
        # (если не понадобится вообще - считать "бесконечно поздно")
        # и вытеснить ту, что понадобится позже всех
        victim = None
        frames[frames.index(victim)] = page
    return faults


def run(fn, refs, n):
    try:
        return fn(refs, n)
    except ValueError as err:
        if "None is not in list" in str(err):  # victim = None - функция ещё не заполнена
            return "TODO"
        raise


if __name__ == "__main__":
    for n in (3, 4):
        print(f"{n} кадра: FIFO={run(fifo, CONTROL, n)}  LRU={run(lru, CONTROL, n)}  Optimal={run(optimal, CONTROL, n)}")
