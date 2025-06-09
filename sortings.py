"""
  copyright 2025, Universität Freiburg

  author: Jakob Haverkamp <jh1444@email.uni-freiburg.de>

  date: 09.06.2025

  description:

"""

import pygame
import sys
import random
import threading
import time
from math import log, log10

pygame.init()

FONT = pygame.font.Font('freesansbold.ttf', 29)

clock = pygame.time.Clock()

width: int = 1900
height: int = 800
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sorts")

sys.setrecursionlimit(5000)

paused: bool = False
is_shuffled: bool = False
is_marked: bool = False
stop_threads: bool = False

cyclecounter: int = 0
marked: int = -1


# ------------------------------------- Classes -------------------------------------------- #

class Block:
    def __init__(self, value: int, amount: int):
        self.amount: int = amount
        self.value: int = value
        self.width: float = (width * 7) / (8 * amount)
        self.yscale: float = (height - 200) / amount

    def draw(self, win, x: float, color: tuple[int, int, int]):
        pygame.draw.rect(win, color, (x, height - 100 - self.value * self.yscale, self.width, self.value * self.yscale))

    def __gt__(self, other: "Block"):
        return self.value > other.value

    def __ge__(self, other: "Block"):
        return self.value >= other.value


# --------------------------------------- Utility Functions ----------------------------------------- #


def time_millies(clock: pygame.time.Clock, start: int) -> int:
    return clock.get_time() - start


def render(array: list[Block], marked: int, done: bool) -> None:
    window.fill((52, 52, 52))

    for x, block in enumerate(array):
        if not done:
            if x == marked:
                block.draw(window, width / 16 + (x * block.width), (150, 10, 10))
            else:
                block.draw(window, width / 16 + (x * block.width), (200, 200, 200))
        else:
            if x <= marked:
                block.draw(window, width / 16 + (x * block.width), (10, 150, 10))
            else:
                block.draw(window, width / 16 + (x * block.width), (200, 200, 200))
    # x-axis
    pygame.draw.rect(window, (25, 25, 25), (width / 16, height - 102, width * 7 / 8, 7))

    if cyclecounter != 0:
        window.blit(FONT.render(f"Cycle: {cyclecounter}", True, (222, 222, 222)), (650, 10))


def quit() -> None:
    global stop_threads
    stop_threads = True
    if threading.active_count() == 2:
        threading.enumerate()[1].join()
    pygame.quit()
    sys.exit()


def pause() -> None:
    global paused
    global clock
    paused = True
    window.blit(FONT.render("<Pause> ", True, (222, 222, 222)), (320, 10))
    pygame.display.flip()
    while (paused):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                paused = False

        pygame.time.wait(10)


def is_sorted(array: list[Block]) -> bool:
    for ind in range(len(array) - 2):
        if array[ind] > array[ind + 1]:
            return False
    return True


def mark_sorted(array: list[Block]):
    global marked
    global clock
    global is_marked

    mark_thread = threading.Thread(target=mark_sorted_thread, args=(len(array),))
    mark_thread.start()

    while not is_marked:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                pause()

        render(array, marked, True)
        window.blit(FONT.render("<Checking> ", True, (222, 222, 222)), (450, 10))
        pygame.display.flip()
        clock.tick(80)

    pygame.time.wait(100)
    render(array, marked, True)
    window.blit(FONT.render("<Checking> ", True, (222, 222, 222)), (450, 10))
    pygame.display.flip()

    is_marked = False
    mark_thread.join()


def mark_sorted_thread(len: int):
    global marked
    global is_marked
    for mark in range(len):
        marked = mark
        clock.tick(len / 1.9)
        while paused and not stop_threads:
            pygame.time.wait(2)
    marked = -1
    is_marked = True


def shuffle(array: list[Block]) -> None:
    global is_shuffled
    global clock
    shuffle_thread = threading.Thread(target=shuffle_array, args=(array,))
    shuffle_thread.start()
    while not is_shuffled:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                pause()

        render(array, marked, False)
        window.blit(FONT.render("<Shuffeling> ", True, (222, 222, 222)), (450, 10))
        pygame.display.flip()
        clock.tick(60)
    shuffle_thread.join()


def shuffle_array(array: list[Block]):
    global marked
    global is_shuffled
    global clock
    array2: list[Block] = []
    array2 += array
    random.shuffle(array2)
    for ind in range(len(array)):
        if stop_threads:
            break
        while paused and not stop_threads:
            pygame.time.wait(2)
        marked = ind
        array[ind] = array2[ind]
        clock.tick(len(array) / 2)

    is_shuffled = True


# -------------------------------------- Sorting Algorithms ------------------------------------------------- #


def sort(algo: int, array: list[Block], time: int = -1) -> threading.Thread:
    match(algo):
        case 0:
            sort_thread = threading.Thread(target=bubblesort, args=(array, time))
            sort_thread.start()
        case 1:
            sort_thread = threading.Thread(target=selectionsort, args=(array, time))
            sort_thread.start()
        case 2:
            if time == 0:
                sort_thread = threading.Thread(target=merge_sort, args=(array,))
            else:
                sort_thread = threading.Thread(target=merge_sort_in_place, args=(array, 0, len(array) - 1, time))
            sort_thread.start()
        case 3:
            sort_thread = threading.Thread(target=quicksort_in_place, args=(array, 0, len(array) - 1, time))
            sort_thread.start()
        case 4:
            if len(array) > 9:
                sort_thread = threading.Thread(target=shufflesort, args=(array, 0))
                sort_thread.start()
            else:
                sort_thread = threading.Thread(target=shufflesort, args=(array, time))
                sort_thread.start()
        case 5:
            sort_thread = threading.Thread(target=insertion_sort, args=(array, time))
            sort_thread.start()
        case 6:
            sort_thread = threading.Thread(target=quicksort_selection, args=(array, 0, len(array) - 1, time))
            sort_thread.start()
        case nr:
            assert False, f"{nr} ist kein Algorithmus"
    return sort_thread


def bubblesort(array: list[Block], delaytime: int = -1):
    global marked
    global cyclecounter
    global paused
    if delaytime == -1:
        delaytime = int(500000 / (len(array)**1.5))
    for ind1 in range(len(array) - 1):
        if stop_threads:
            break
        while paused:
            pygame.time.delay(2)
        for ind in range(len(array) - ind1 - 1):
            if stop_threads:
                break
            if not (array[ind] < array[ind + 1]):
                help = array[ind]
                array[ind] = array[ind + 1]
                array[ind + 1] = help
            marked = ind + 1
        pygame.time.delay(delaytime)
        cyclecounter += 1


def selectionsort(array: list[Block], delaytime: int = -1):
    global marked
    global cyclecounter
    global paused
    highestind: int
    if delaytime == -1:
        delaytime = int(400000 / (len(array)**1.5))
    for ind1 in range(len(array) - 1):
        if stop_threads:
            break
        while paused and not stop_threads:
            pygame.time.wait(2)
        highestind = 0

        for ind in range(len(array) - ind1):
            if stop_threads:
                break
            if array[ind] > array[highestind]:
                highestind = ind
            marked = highestind
        pygame.time.delay(delaytime)

        array[-ind1 - 1], array[highestind] = array[highestind], array[-ind1 - 1]
        cyclecounter += 1


def merge_sort_in_place(array: list[Block], start: int, end: int, delaytime: int = -1):
    global paused
    global marked
    global cyclecounter
    cyclecounter += 1

    if stop_threads:
        return []

    if delaytime == -1:
        delaytime = int(30000 / (len(array) * log(len(array))))

    while paused and not stop_threads:
        pygame.time.delay(2)

    if end - start > 1:
        # Mitte der Liste berechnen
        mid = (start + end) // 2

        # Linke und rechte Hälfte sortieren
        marked = mid
        merge_sort_in_place(array, start, mid, delaytime)
        marked = mid
        merge_sort_in_place(array, mid, end, delaytime)

        # Sortierte Hälften in-place zusammenführen
        merge_in_place(array, start, mid, end, delaytime)


def merge_in_place(array: list[Block], start: int, mid: int, end: int, delaytime: int):
    global marked
    global paused

    # Indizes für die zwei Hälften
    left = start
    right = mid

    while left < right and right < end:
        if stop_threads:
            break
        pygame.time.delay(delaytime)
        while paused and not stop_threads:
            pygame.time.wait(2)
        marked = left
        if array[left] <= array[right]:
            # Das Element links ist bereits korrekt
            left += 1
        else:
            # Element aus der rechten Hälfte an die richtige Position schieben
            temp = array[right]
            # Alle Elemente zwischen `left` und `right` verschieben
            array[left + 1:right + 1] = array[left:right]
            array[left] = temp

            # Indizes aktualisieren
            left += 1
            right += 1


def quicksort_in_place(array: list[Block], low: int, high: int, delaytime: int):
    global paused
    global marked
    global cyclecounter
    cyclecounter += 1

    if stop_threads:
        return []

    if delaytime == -1:
        delaytime = int(30000 / (len(array) * log(len(array))))

    while paused and not stop_threads:
        pygame.time.delay(2)

    if low < high:
        # Partitioniere die Liste und erhalte den Index des Pivots

        # Zufälligen Pivot auswählen
        pivot_index = random.randint(low, high)
        array[pivot_index], array[high] = array[high], array[pivot_index]  # Tausche Pivot mit dem letzten Element

        pivot_index = partition(array, low, high, delaytime)

        # Rekursiver Aufruf für die linken und rechten Teilbereiche
        quicksort_in_place(array, low, pivot_index - 1, delaytime)
        quicksort_in_place(array, pivot_index + 1, high, delaytime)


def quicksort_selection(array: list[Block], low: int, high: int, delaytime: int):
    global paused
    global marked
    global cyclecounter
    cyclecounter += 1

    if stop_threads:
        return []

    if delaytime == -1:
        delaytime = int(30000 / (len(array) * log(len(array))))

    while paused and not stop_threads:
        pygame.time.delay(2)

    if high - low <= 16:
        selection_part(array, low, high)

    elif low < high:
        # Partitioniere die Liste und erhalte den Index des Pivots

        # Zufälligen Pivot auswählen
        pivot_index = random.randint(low, high)
        array[pivot_index], array[high] = array[high], array[pivot_index]  # Tausche Pivot mit dem letzten Element

        pivot_index = partition(array, low, high, delaytime)

        # Rekursiver Aufruf für die linken und rechten Teilbereiche
        quicksort_in_place(array, low, pivot_index - 1, delaytime)
        quicksort_in_place(array, pivot_index + 1, high, delaytime)


def selection_part(array: list[Block], low: int, high: int):
    global marked
    global cyclecounter
    global paused
    highestind: int
    for ind1 in range(low - high):
        if stop_threads:
            break
        while paused and not stop_threads:
            pygame.time.wait(2)
        highestind = low
        for ind in range(low - high - ind1):
            if stop_threads:
                break
            if array[ind] > array[highestind]:
                highestind = ind
            marked = highestind

        array[-ind1 - 1], array[highestind] = array[highestind], array[-ind1 - 1]
        cyclecounter += 1


def partition(array: list[Block], low: int, high: int, delaytime: int):
    global paused
    global marked
    # Wähle das letzte Element als Pivot
    pivot = array[high]
    i = low - 1  # Index des kleineren Elements

    for j in range(low, high):
        pygame.time.delay(delaytime)
        while paused and not stop_threads:
            pygame.time.wait(2)
        # Wenn aktuelles Element kleiner oder gleich Pivot ist
        if array[j] <= pivot:
            i += 1
            # Elemente an Index i und j vertauschen
            array[i], array[j] = array[j], array[i]
        marked = i

    # Platziere das Pivot-Element an die richtige Position
    array[i + 1], array[high] = array[high], array[i + 1]
    return i + 1


def shufflesort(array: list[Block], delaytime: int):
    global cyclecounter
    global stop_threads
    global marked
    if delaytime == -1:
        delaytime = 1

    while not (is_sorted(array) or stop_threads):
        marked = random.randint(0, len(array) - 1)
        cyclecounter += 1
        random.shuffle(array)


def insertion_sort(array: list[Block], delaytime: int):
    global paused
    global marked
    global cyclecounter

    if delaytime == -1:
        delaytime = int(60000 / (len(array) * log10(len(array))))

    for ind in range(1, len(array)):
        pygame.time.delay(delaytime)
        while paused and not stop_threads:
            pygame.time.wait(2)
        if stop_threads:
            break
        cyclecounter += 1
        key = array[ind]  # Aktuelles Element
        ind2 = ind - 1

        # Verschiebe alle größeren Elemente nach rechts
        while ind2 >= 0 and array[ind2] > key and not stop_threads:

            array[ind2 + 1] = array[ind2]
            ind2 -= 1
            marked = ind2

        # Füge das aktuelle Element an der richtigen Stelle ein
        array[ind2 + 1] = key


def merge_sort(array: list[Block]):
    # Basisfall: Eine Liste mit einem oder keinem Element ist sortiert.
    if len(array) <= 1:
        return array

    # Liste in zwei Hälften teilen
    mid = len(array) // 2
    left_half = merge_sort(array[:mid])
    right_half = merge_sort(array[mid:])

    # Sortierte Hälften zusammenführen
    return merge(left_half, right_half)


def merge(left, right):
    sorted_list = []
    i = j = 0

    # Elemente aus beiden Listen in sortierter Reihenfolge zusammenfügen
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1

    # Verbleibende Elemente (falls vorhanden) hinzufügen
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])

    return sorted_list

# ------------------------------------ Main Function -------------------------------------------------- #


def main(amount: int, algo: int = 0) -> None:
    global clock
    global cyclecounter
    global marked

    runnin: bool = False
    done: bool = False

    arraycopy: list[Block] = []
    array: list[Block] = []

    STOPEVENT = pygame.USEREVENT + 1

    for i in range(amount):
        array.append(Block(i + 1, amount))

    while not runnin:

        render(array, -1, False)

        window.blit(FONT.render("<Press Any Key to Start Simulation> ", True, (222, 222, 222)), (150, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if not done:
                    shuffle(array)
                    arraycopy += array
                    done = True
                else:
                    runnin = True
                    done = False

        pygame.display.flip()
        clock.tick(60)


# --------------------------------------- Main Loop ------------------------------------------------ #

    while runnin:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and not done:
                pause()
            if event.type == STOPEVENT:
                if done:
                    runnin = False

        if cyclecounter == 0:
            sort_thread = sort(algo, array)
            cyclecounter += 1

        if not done:
            if is_sorted(array):
                done = True
                mark_sorted(array)
                start_time = time.monotonic()
                cycles = cyclecounter
                sort_thread = sort(algo, arraycopy, 0)
                sort_thread.join()
                marked = -1
                cyclecounter = cycles
                runtime = (time.monotonic() - start_time) * 1000
                pygame.time.set_timer(STOPEVENT, 5000)

        render(array, marked, done)

        if done and not paused:
            window.blit(FONT.render(f"<done in {runtime:2f} ms> ", True, (222, 222, 222)), (300, 10))
            sort_thread.join()

        pygame.display.flip()
        clock.tick(60)

    cyclecounter = 0
    main(amount, algo)


if __name__ == "__main__":
    match sys.argv[1:]:
        case ['bubble', amount]:
            main(int(amount), 0)
        case ['selection', amount]:
            main(int(amount), 1)
        case ['merge', amount]:
            main(int(amount), 2)
        case ['quick', amount]:
            main(int(amount), 3)
        case ['shufflesort', amount]:
            main(int(amount), 4)
        case ['insert', amount]:
            main(int(amount), 5)
        case ['quickselect', amount]:
            main(int(amount), 6)
        case ['bubble']:
            main(int(width * 7 // 8), 0)
        case ['selection']:
            main(int(width * 7 // 8), 1)
        case ['merge']:
            main(int(width * 7 // 8), 2)
        case ['quick']:
            main(int(width * 7 // 8), 3)
        case ['shufflesort']:
            main(int(width * 7 // 8), 4)
        case ['insert']:
            main(int(width * 7 // 8), 5)
        case ['quickselect']:
            main(int(width * 7 // 8), 6)
        case _:
            main(width * 7 // 8, 5)
