# Проектирование операционных систем

Полный репозиторий курса: **16 практических работ**, проект первого модуля, результаты запусков и автоматическая проверка на Ubuntu.

Автор: [zeuscode-tech](https://github.com/zeuscode-tech)

## Практические работы

| № | Тема | Что реализовано |
|---:|---|---|
| 1 | [Пользователи, группы и права](pr01/) | users/groups, mode bits, setgid |
| 2 | [Bash и системные вызовы](pr02/) | анализ журналов, `strace`, `cat` против Python |
| 3 | [Процессы Linux](pr03/) | `/proc`, fork, exec, wait, zombie, orphan, CoW |
| 4 | [Потоки](pr04/) | CPU/I/O-bound эксперименты, GIL, процессы против потоков |
| 5 | [Планирование CPU](pr05/) | FCFS, SJF, SRTF, Priority, RR, aging |
| 6 | [Синхронизация](pr06/) | race condition, mutex, semaphore, condition, barrier |
| 7 | [IPC](pr07/) | Pipe, FIFO, Unix socket, shared memory |
| 8 | [Взаимоблокировки](pr08/) | банкир, wait-for graph, TrackedLock, философы |
| 9 | [Непрерывное распределение памяти](practice%20-%209/) | first/best/worst fit, coalescing, buddy, C allocator |
| 10 | [Страницы, таблицы и TLB](pr10/) | трансляция адресов, EAT, TLB, многоуровневая таблица |
| 11 | [Виртуальная память](practice%20-%2011/) | FIFO, LRU, Optimal, Clock, Белади, реальные page faults |
| 12 | [Файловые системы](pr12/) | inode, ссылки, backup, дедупликация, размещение, FUSE |
| 13 | [Планирование диска](pr13/) | FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK, fio |
| 14 | [Подсистема ввода-вывода](pr14/) | буферизация, blocking I/O, page cache, O_DIRECT, модуль ядра |
| 15 | [Защита и виртуализация](pr15/) | права, Docker, namespaces, cgroups, контейнер с нуля |
| 16 | [Итоговая защита](pr16/) | чек-лист, подготовка к РК‑2, проверка сдачи |

Каждая папка содержит README с целью, запуском, результатами, выводами и ограничениями.

## Проект модуля 1

[«Взаимоблокировки в банке»](modul1/) объединяет уровни A, B и C:

- диагностика deadlock через `faulthandler`;
- исправление единым порядком захвата;
- алгоритм банкира и проверка запросов;
- граф ожидания и поиск цикла;
- `TrackedLock` и три варианта задачи философов;
- [PDF-презентация](modul1/presentation/project2-deadlocks-presentation.pdf).

```bash
./modul1/run_all.sh
```

## Быстрая проверка

```bash
python3 check_all.py
python3 pr16/check_submission.py
```

Та же проверка запускается GitHub Actions на Ubuntu. Она контролирует структуру, локальные ссылки, синтаксис Python/Bash/C и ключевые контрольные результаты.

## Требования

- Ubuntu 22.04+ для Linux-специфичных экспериментов;
- Python 3.11+, Bash, Git и C compiler;
- `strace`, `rsync`; для отдельных работ — `matplotlib`, `fio`, Docker, FUSE3;
- root требуется только для явно отмеченных демонстраций в учебной VM.

Базовая установка:

```bash
sudo apt update
sudo apt install -y python3 python3-venv build-essential git strace rsync
```

## Структура

```text
operating-systems-practices/
├── pr01/ … pr08/
├── practice - 9/
├── pr10/
├── practice - 11/
├── pr12/ … pr16/
├── modul1/
├── .github/workflows/check.yml
├── check_all.py
└── README.md
```

Привилегированные сценарии не входят в автоматический запуск: они проверяются статически и запускаются вручную только в изолированной Ubuntu.
