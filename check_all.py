#!/usr/bin/env python3
"""Воспроизводимая проверка практических работ и проекта модуля 1."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(command: list[str], cwd: Path, expected: tuple[str, ...] = ()) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=30,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        raise RuntimeError(
            f"Команда завершилась с кодом {result.returncode}: "
            f"{' '.join(command)}\n{output}"
        )
    for fragment in expected:
        if fragment not in output:
            raise AssertionError(
                f"В выводе {' '.join(command)} нет строки: {fragment!r}"
            )
    return output


def check_structure() -> None:
    for number in range(1, 9):
        directory = ROOT / f"pr{number:02d}"
        assert directory.is_dir(), f"Нет каталога {directory.name}"
        assert (directory / "README.md").is_file(), (
            f"Нет {directory.name}/README.md"
        )

    module = ROOT / "modul1"
    required = [
        "README.md",
        "DEFENSE_GUIDE.md",
        "run_all.sh",
        "transfer_deadlock.py",
        "transfer_fixed.py",
        "banker.py",
        "wait_graph.py",
        "tracked_lock.py",
        "transfer_tracked.py",
        "philosophers.py",
        "test_project.py",
        "data/bank_state.txt",
        "data/bank_state2.txt",
        "data/requests.txt",
        "data/waitlog.txt",
        "presentation/project2-deadlocks-presentation.pdf",
    ]
    for relative in required:
        assert (module / relative).is_file(), f"Нет modul1/{relative}"
    assert (module / "presentation/project2-deadlocks-presentation.pdf").stat().st_size > 100_000, (
        "PDF-презентация подозрительно мала"
    )


def check_markdown_links() -> None:
    readmes = [
        ROOT / "README.md",
        *sorted(ROOT.glob("pr*/README.md")),
        ROOT / "modul1/README.md",
    ]
    broken: list[str] = []
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for readme in readmes:
        text = readme.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            target = target.strip().split()[0].strip("<>")
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            relative = urllib.parse.unquote(target.split("#", 1)[0])
            if relative and not (readme.parent / relative).exists():
                broken.append(f"{readme.relative_to(ROOT)} -> {target}")
    assert not broken, "Битые ссылки:\n" + "\n".join(broken)


def check_python_syntax() -> None:
    paths = [*ROOT.glob("pr*/*.py"), *ROOT.glob("modul1/*.py")]
    for path in sorted(paths):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def check_programs() -> None:
    run(["bash", "-n", "report.sh"], ROOT / "pr02")
    run(
        ["./report.sh", "data", "ERROR", "--top", "3"],
        ROOT / "pr02",
        ("db", "net", "disk"),
    )
    run([sys.executable, "hello.py"], ROOT / "pr02", ("19076",))
    run(
        [sys.executable, "runner.py", "2", "sh", "-c", "exit 7"],
        ROOT / "pr03",
        ("код=7",),
    )
    run(
        [sys.executable, "sched.py", "--algo", "srtf", "set1.txt"],
        ROOT / "pr05",
        ("Среднее ожидание: 6.50", "Средний оборот: 13.00"),
    )
    run(
        [
            sys.executable,
            "sched.py",
            "--algo",
            "rr",
            "--quantum",
            "3",
            "set1.txt",
        ],
        ROOT / "pr05",
        ("Среднее ожидание: 13.50", "Средний оборот: 20.00"),
    )
    run(
        [sys.executable, "semaphore_buffer.py"],
        ROOT / "pr06",
        ("Каждый элемент ровно один раз: True",),
    )
    run(
        [sys.executable, "condition_buffer.py"],
        ROOT / "pr06",
        ("Инварианты буфера соблюдены: True",),
    )
    run(
        [sys.executable, "barrier_demo.py"],
        ROOT / "pr06",
        ("Все фазы выполнены корректно: True",),
    )

    banker = subprocess.run(
        [sys.executable, "banker.py", "bank1.txt"],
        cwd=ROOT / "pr08",
        input="safe\nquit\n",
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert banker.returncode == 0, banker.stderr
    assert "P1 -> P3 -> P4 -> P2 -> P0" in banker.stdout
    run(
        [sys.executable, "wait_graph.py", "events_deadlock.txt"],
        ROOT / "pr08",
        ("Взаимоблокировка обнаружена: True", "Участники: P1, P2"),
    )
    run(
        [sys.executable, "philosophers_fixed.py"],
        ROOT / "pr08",
        ("Взаимоблокировки нет: True",),
    )

    module = ROOT / "modul1"
    run(["bash", "-n", "run_all.sh"], module)
    run(
        [sys.executable, "-m", "unittest", "-v", "test_project.py"],
        module,
        ("Ran 4 tests", "OK"),
    )
    run(
        [sys.executable, "transfer_fixed.py"],
        module,
        ("Инвариант суммы соблюдён: True", "циклическое ожидание"),
    )
    run(
        [
            sys.executable,
            "banker.py",
            "data/bank_state.txt",
            "data/bank_state2.txt",
            "--requests",
            "data/requests.txt",
        ],
        module,
        ("Состояние: SAFE", "Состояние: UNSAFE", "P4 [2, 0, 0]: ERROR"),
    )
    run(
        [sys.executable, "wait_graph.py", "data/waitlog.txt"],
        module,
        ("участники: P3, P4, P5", "не входят в него: P7"),
    )
    run(
        [sys.executable, "transfer_tracked.py"],
        module,
        ("Обнаружено циклов: 1", "Сумма сохранена: True"),
    )
    run(
        [sys.executable, "philosophers.py", "--duration", "0.2"],
        module,
        ("Наивный вариант", "Упорядоченный захват вилок", "Официант"),
    )


def main() -> None:
    checks = [
        ("Структура pr01–pr08 и modul1", check_structure),
        ("Локальные ссылки README", check_markdown_links),
        ("Синтаксис Python", check_python_syntax),
        ("Ключевые запуски", check_programs),
    ]
    for title, function in checks:
        function()
        print(f"[OK] {title}")
    print("Все автоматические проверки пройдены.")


if __name__ == "__main__":
    main()
