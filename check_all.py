#!/usr/bin/env python3
"""Единая безопасная проверка всех практических работ курса."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRACTICES = {
    1: "pr01", 2: "pr02", 3: "pr03", 4: "pr04",
    5: "pr05", 6: "pr06", 7: "pr07", 8: "pr08",
    9: "practice - 9", 10: "pr10", 11: "practice - 11",
    12: "pr12", 13: "pr13", 14: "pr14", 15: "pr15", 16: "pr16",
}


def run(command: list[str], cwd: Path, expected: tuple[str, ...] = ()) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=60)
    output = result.stdout + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"Код {result.returncode}: {' '.join(command)}\n{output}")
    for fragment in expected:
        if fragment not in output:
            raise AssertionError(f"В выводе {' '.join(command)} нет {fragment!r}\n{output}")
    return output


def check_structure() -> None:
    for number, name in PRACTICES.items():
        directory = ROOT / name
        assert directory.is_dir(), f"Нет ПР-{number}: {name}"
        assert (directory / "README.md").is_file(), f"Нет {name}/README.md"
    module = ROOT / "modul1"
    for relative in (
        "README.md", "run_all.sh", "test_project.py",
        "presentation/project2-deadlocks-presentation.pdf",
    ):
        assert (module / relative).is_file(), f"Нет modul1/{relative}"
    assert (module / "presentation/project2-deadlocks-presentation.pdf").stat().st_size > 100_000


def check_markdown_links() -> None:
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    broken: list[str] = []
    for readme in sorted(ROOT.rglob("*.md")):
        if any(part in {".git", ".venv"} for part in readme.parts):
            continue
        for target in pattern.findall(readme.read_text(encoding="utf-8")):
            target = target.strip().split()[0].strip("<>")
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            relative = urllib.parse.unquote(target.split("#", 1)[0])
            if relative and not (readme.parent / relative).exists():
                broken.append(f"{readme.relative_to(ROOT)} -> {target}")
    assert not broken, "Битые ссылки:\n" + "\n".join(broken)


def check_python_syntax() -> None:
    for path in sorted(ROOT.rglob("*.py")):
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def check_shell_syntax() -> None:
    for path in sorted(ROOT.rglob("*.sh")):
        if ".git" not in path.parts:
            run(["bash", "-n", str(path)], ROOT)


def check_c_syntax() -> None:
    compiler = subprocess.run(["sh", "-c", "command -v cc"], text=True, capture_output=True)
    if compiler.returncode != 0:
        print("[SKIP] C compiler не найден")
        return
    for path in sorted(ROOT.rglob("*.c")):
        if "kernel_module" in path.parts:
            continue
        run(["cc", "-std=c11", "-Wall", "-Wextra", "-fsyntax-only", str(path)], ROOT)


def check_original_practices() -> None:
    run(["./report.sh", "data", "ERROR", "--top", "3"], ROOT / "pr02", ("db", "net", "disk"))
    run([sys.executable, "hello.py"], ROOT / "pr02", ("19076",))
    run([sys.executable, "runner.py", "2", "sh", "-c", "exit 7"], ROOT / "pr03", ("код=7",))
    run([sys.executable, "sched.py", "--algo", "srtf", "set1.txt"], ROOT / "pr05", ("Среднее ожидание: 6.50",))
    run([sys.executable, "sched.py", "--algo", "rr", "--quantum", "3", "set1.txt"], ROOT / "pr05", ("Среднее ожидание: 13.50",))
    run([sys.executable, "semaphore_buffer.py"], ROOT / "pr06", ("ровно один раз: True",))
    run([sys.executable, "condition_buffer.py"], ROOT / "pr06", ("Инварианты буфера соблюдены: True",))
    run([sys.executable, "barrier_demo.py"], ROOT / "pr06", ("Все фазы выполнены корректно: True",))
    run([sys.executable, "wait_graph.py", "events_deadlock.txt"], ROOT / "pr08", ("Взаимоблокировка обнаружена: True",))
    run([sys.executable, "philosophers_fixed.py"], ROOT / "pr08", ("Взаимоблокировки нет: True",))


def check_memory_and_storage() -> None:
    run([sys.executable, "compare.py"], ROOT / "practice - 9", ("best +merge", "buddy"))
    run([sys.executable, "translate.py"], ROOT / "pr10", ("физический адрес 2224", "страница отсутствует"))
    run([sys.executable, "multilevel.py"], ROOT / "pr10", ("Двухуровневая таблица",))
    run([sys.executable, "replace.py"], ROOT / "practice - 11", ("FIFO: 15", "LRU: 12", "Optimal: 9"))
    run([sys.executable, "fs_model.py"], ROOT / "pr12", ("contiguous", "linked", "indexed"))
    run([sys.executable, "disk.py"], ROOT / "pr13", ("FCFS              640", "C-LOOK            322"))
    run([sys.executable, "starvation.py"], ROOT / "pr13", ("Позиция дальнего запроса",))
    run([sys.executable, "fifo_wait.py"], ROOT / "pr14", ("busy waiting", "blocking"))
    run([sys.executable, "-m", "unittest", "-v", "test_app.py"], ROOT / "pr15", ("Ran 3 tests", "OK"))
    run([sys.executable, "check_submission.py"], ROOT / "pr16", ("ПР-1…ПР-16",))

    with tempfile.TemporaryDirectory(prefix="pr12-check-") as temporary:
        root = Path(temporary)
        (root / "a.txt").write_text("одинаково\n", encoding="utf-8")
        (root / "b.txt").write_text("одинаково\n", encoding="utf-8")
        run([sys.executable, str(ROOT / "pr12/dedup.py"), str(root)], ROOT, ("Дубликатов: 1",))


def check_module() -> None:
    module = ROOT / "modul1"
    run([sys.executable, "-m", "unittest", "-v", "test_project.py"], module, ("Ran 4 tests", "OK"))
    run([sys.executable, "transfer_fixed.py"], module, ("Инвариант суммы соблюдён: True",))
    run([sys.executable, "wait_graph.py", "data/waitlog.txt"], module, ("участники: P3, P4, P5",))


def main() -> None:
    checks = [
        ("Структура ПР-1…ПР-16 и modul1", check_structure),
        ("Локальные ссылки Markdown", check_markdown_links),
        ("Синтаксис Python", check_python_syntax),
        ("Синтаксис Bash", check_shell_syntax),
        ("Синтаксис C", check_c_syntax),
        ("ПР-1…ПР-8", check_original_practices),
        ("ПР-9…ПР-16", check_memory_and_storage),
        ("Проект modul1", check_module),
    ]
    for title, function in checks:
        function()
        print(f"[OK] {title}")
    print("Все автоматические проверки пройдены.")


if __name__ == "__main__":
    main()
