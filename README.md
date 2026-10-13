# Проектирование операционных систем

Репозиторий содержит восемь практических работ по дисциплине **«Проектирование операционных систем»**.

Автор: [zeuscode-tech](https://github.com/zeuscode-tech)

## Практические работы

| № | Тема | Основные результаты |
|---:|---|---|
| 1 | [Пользователи, группы и права доступа](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%201) | Пользователи Linux, группы и права на общий каталог |
| 2 | [Bash и системные вызовы](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%202) | Обработка журналов, Bash, `strace`, сравнение `cat` и Python |
| 3 | [Процессы в Linux](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%203) | `fork`, `exec`, `wait`, дерево процессов, зомби, сироты и Copy-on-Write |
| 4 | [Потоки](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%204) | Сравнение потоков и процессов для CPU-bound и I/O-bound задач |
| 5 | [Симулятор планирования CPU](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%205) | FCFS, SJF, SRTF, Priority, Round Robin, метрики и aging |
| 6 | [Синхронизация](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%206) | Гонки, мьютексы, семафоры, условные переменные и барьер |
| 7 | [Межпроцессное взаимодействие](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%207) | FIFO, Unix-сокеты, Pipe и разделяемая память |
| 8 | [Взаимоблокировки](https://github.com/zeuscode-tech/operating-systems-practices/tree/main/practice%20-%208) | Алгоритм банкира, граф ожидания, TrackedLock и философы |

## Краткое содержание

### Практическая работа №1 — пользователи и права

Работа с Ubuntu Linux, пользователями, группами, владельцами файлов и разрешениями общего каталога.

### Практическая работа №2 — Bash и системные вызовы

Сценарий для анализа журналов по уровням ERROR и WARN, режим `--top` и обработка ошибок. Через `strace` исследованы системные вызовы Python и `cat`.

### Практическая работа №3 — процессы

Построено дерево процессов по данным `/proc`. Реализован запуск через `fork` и `exec`. Воспроизведены зомби и сирота, исследован Copy-on-Write.

### Практическая работа №4 — потоки

Сравнены один поток, четыре потока и четыре процесса в вычислительной и сетевой задачах. Показано влияние GIL и различие в использовании памяти.

### Практическая работа №5 — планирование CPU

Реализованы FCFS, SJF, SRTF, Priority и Round Robin. Рассчитаны ожидание, оборот, отклик, загрузка CPU и переключения. Исследованы квант RR и старение приоритетов.

### Практическая работа №6 — синхронизация

Воспроизведено состояние гонки. «Производитель–потребитель» реализован на семафорах и условной переменной. Показана ошибка `if` вместо `while` при ожидании.

### Практическая работа №7 — IPC

Реализованы клиент–сервер через FIFO и Unix-сокеты. Передача массива через Pipe сравнена с `multiprocessing.shared_memory`.

### Практическая работа №8 — взаимоблокировки

Реализованы алгоритм банкира с откатом запросов, DFS-поиск цикла в графе ожидания и `TrackedLock`. Задача философов исправлена двумя способами.

## Используемые технологии

- Ubuntu Linux
- Python 3
- Bash
- Git и GitHub
- `/proc` и `strace`
- `threading` и `multiprocessing`
- FIFO и Unix domain sockets
- Pipe и Shared Memory

## Структура репозитория

```text
operating-systems-practices/
├── practice - 1/
├── practice - 2/
├── practice - 3/
├── practice - 4/
├── practice - 5/
├── practice - 6/
├── practice - 7/
├── practice - 8/
└── README.md
```

Внутри каждой практической находятся исходный код, инструкция по запуску, результаты проверок и подробные выводы.
