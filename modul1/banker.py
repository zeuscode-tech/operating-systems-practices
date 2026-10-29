"""Алгоритм банкира и обработка запросов ресурсов для варианта 2."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


Vector = list[int]


@dataclass
class BankState:
    available: Vector
    allocation: dict[str, Vector]
    maximum: dict[str, Vector]

    @property
    def pids(self) -> list[str]:
        return list(self.allocation)

    @property
    def need(self) -> dict[str, Vector]:
        return {
            pid: [maximum - allocated for maximum, allocated in zip(self.maximum[pid], self.allocation[pid])]
            for pid in self.pids
        }

    def copy(self) -> "BankState":
        return BankState(
            self.available.copy(),
            {pid: values.copy() for pid, values in self.allocation.items()},
            {pid: values.copy() for pid, values in self.maximum.items()},
        )


@dataclass
class SafetyResult:
    safe: bool
    sequence: list[str]
    unfinished: list[str]
    final_work: Vector


@dataclass
class RequestResult:
    status: str
    reason: str
    sequence: list[str]


def clean_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def parse_state(path: Path) -> BankState:
    lines = clean_lines(path)
    sections: dict[str, list[str]] = {"Available": [], "Allocation": [], "Max": []}
    current: str | None = None
    for line in lines:
        if line.endswith(":"):
            current = line[:-1]
            if current not in sections:
                raise ValueError(f"Неизвестная секция {current!r}")
            continue
        if current is None:
            raise ValueError(f"Строка вне секции: {line}")
        sections[current].append(line)

    if len(sections["Available"]) != 1:
        raise ValueError("Секция Available должна содержать одну строку")

    available = [int(value) for value in sections["Available"][0].split()]

    def parse_process_rows(rows: Iterable[str]) -> dict[str, Vector]:
        result: dict[str, Vector] = {}
        for row in rows:
            pid, *numbers = row.split()
            values = [int(value) for value in numbers]
            if len(values) != len(available):
                raise ValueError(f"Неверное число ресурсов для {pid}")
            result[pid] = values
        return result

    allocation = parse_process_rows(sections["Allocation"])
    maximum = parse_process_rows(sections["Max"])
    if allocation.keys() != maximum.keys():
        raise ValueError("Списки процессов Allocation и Max различаются")
    for pid in allocation:
        if any(a > m for a, m in zip(allocation[pid], maximum[pid])):
            raise ValueError(f"Allocation превышает Max для {pid}")
    return BankState(available, allocation, maximum)


def safety_check(state: BankState) -> SafetyResult:
    work = state.available.copy()
    finish = {pid: False for pid in state.pids}
    need = state.need
    sequence: list[str] = []

    while True:
        progressed = False
        for pid in state.pids:
            if finish[pid]:
                continue
            if all(required <= current for required, current in zip(need[pid], work)):
                work = [current + released for current, released in zip(work, state.allocation[pid])]
                finish[pid] = True
                sequence.append(pid)
                progressed = True
        if not progressed:
            break

    unfinished = [pid for pid, completed in finish.items() if not completed]
    return SafetyResult(not unfinished, sequence, unfinished, work)


def evaluate_request(original: BankState, pid: str, request: Vector) -> RequestResult:
    if pid not in original.allocation:
        return RequestResult("ERROR", f"неизвестный процесс {pid}", [])
    if len(request) != len(original.available) or any(value < 0 for value in request):
        return RequestResult("ERROR", "некорректный вектор запроса", [])

    need = original.need[pid]
    if any(value > remaining for value, remaining in zip(request, need)):
        return RequestResult(
            "ERROR",
            f"запрос {request} превышает объявленную потребность {need}",
            [],
        )
    if any(value > available for value, available in zip(request, original.available)):
        return RequestResult(
            "WAIT",
            f"сейчас доступно только {original.available}",
            [],
        )

    trial = original.copy()
    trial.available = [available - value for available, value in zip(trial.available, request)]
    trial.allocation[pid] = [allocated + value for allocated, value in zip(trial.allocation[pid], request)]
    result = safety_check(trial)
    if result.safe:
        return RequestResult(
            "GRANT",
            "после выдачи сохраняется безопасная последовательность",
            result.sequence,
        )
    return RequestResult(
        "REFUSE",
        "после выдачи состояние становится небезопасным, выполнен откат",
        [],
    )


def parse_requests(path: Path) -> list[tuple[str, Vector]]:
    requests: list[tuple[str, Vector]] = []
    for line in clean_lines(path):
        pid, *numbers = line.split()
        requests.append((pid, [int(value) for value in numbers]))
    return requests


def print_state_result(path: Path, state: BankState) -> None:
    result = safety_check(state)
    print(f"Файл: {path.name}")
    print("Available:", state.available)
    print("Need:")
    for pid, need in state.need.items():
        print(f"  {pid}: {need}")
    print("Состояние:", "SAFE" if result.safe else "UNSAFE")
    if result.sequence:
        print("Выполнимая часть последовательности:", " -> ".join(result.sequence))
    if result.unfinished:
        print("Не могут завершиться:", ", ".join(result.unfinished))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Алгоритм банкира для проекта 2")
    parser.add_argument("states", nargs="+", type=Path, help="Файлы состояний")
    parser.add_argument("--requests", type=Path, help="Файл запросов для первого состояния")
    args = parser.parse_args()

    states = [parse_state(path) for path in args.states]
    for path, state in zip(args.states, states):
        print_state_result(path, state)

    if args.requests:
        original = states[0]
        print(f"Запросы из {args.requests.name}; каждый проверяется относительно исходного состояния")
        for pid, request in parse_requests(args.requests):
            result = evaluate_request(original, pid, request)
            print(f"{pid} {request}: {result.status} — {result.reason}")
            if result.sequence:
                print("  Безопасная последовательность:", " -> ".join(result.sequence))


if __name__ == "__main__":
    main()
