import matplotlib.pyplot as plt

methods = [
    "First + merge",
    "Best + merge",
    "Worst + merge",
    "Buddy",
]

refusals = [33, 32, 38, 38]
external = [0.47, 0.36, 0.52, 0.36]
internal = [0, 0, 0, 175]

colors = ["#4C78A8", "#59A14F", "#E15759", "#F28E2B"]

figure, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].bar(methods, refusals, color=colors)
axes[0].set_title("Количество отказов")
axes[0].set_ylabel("Отказы")

axes[1].bar(methods, external, color=colors)
axes[1].set_title("Внешняя фрагментация")
axes[1].set_ylabel("Средняя доля")

axes[2].bar(methods, internal, color=colors)
axes[2].set_title("Внутренняя фрагментация")
axes[2].set_ylabel("Среднее значение")

for axis in axes:
    axis.tick_params(axis="x", rotation=25)
    axis.grid(axis="y", alpha=0.3)

figure.suptitle("Сравнение алгоритмов распределения памяти на ops2")
figure.tight_layout()

plt.savefig("ops2_comparison.png", dpi=160, bbox_inches="tight")

print("Создан файл: ops2_comparison.png")
