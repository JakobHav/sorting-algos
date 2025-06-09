import time


def cycle_bubblesort(array: list[int], cycle: int = 0):
    for ind in range(len(array) - 1):
        if not (array[ind] < array[ind + 1]):
            help = array[ind]
            array[ind] = array[ind + 1]
            array[ind + 1] = help


array1 = [1, 3, 32, 33, 4, 55, 6, 7, 8, 9]
cycle_bubblesort(array1)
print(array1)
cycle_bubblesort(array1)
print(array1)
cycle_bubblesort(array1)
print(array1)
cycle_bubblesort(array1)
print(array1)
cycle_bubblesort(array1)
print(array1)
