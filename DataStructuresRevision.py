def bubble_sort(lst):
    n = len(lst)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if lst[j] < lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                swapped = True
        if not swapped:
            break

def selection_sort(lst):
    n = len(lst)
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            if lst[j] < lst[smallest]:
                smallest = j
        if smallest != i:
            lst[smallest], lst[i] = lst[i], lst[smallest]

def insertion_sort(lst):
    n = len(lst)
    for i in range(1, n):
        temp = lst[i]
        j = i - 1
        while j >= 0 and lst[j] > temp:
            lst[j + 1] = lst[j]
            j -= 1
        lst[j + 1] = temp

def merge(lst, left_half, right_half):
    i = j = k = 0
    n1, n2 = len(left_half), len(right_half)
    while i < n1 and j < n2:
        if left_half[i] <= right_half[j]:
            lst[k] = left_half[i]
            i += 1
        else:
            lst[k] = right_half[j]
            j += 1
        k += 1

        while i < n1:
            lst[k] = lst[i]
            i += 1
            k += 1

        while j < n2:
            lst[k] = lst[j]
            j += 1
            k += 1

    return lst

def merge_sort(lst):
    start, end = 0, len(lst) - 1
    while start < end:
        mid = (start + end) // 2
        left_half = merge_sort(lst[:mid])
        right_half = merge_sort(lst[mid:])
        merge(lst, left_half, right_half)
    return lst

def partition(lst):
    n = len(lst)
    pivot = 0
    i, j = 1, n - 1
    while True:
        while i <= j and lst[i] <= lst[pivot]:
            i += 1
        while i <= j and lst[j] > lst[pivot]:
            j -= 1

        if j < i:
            break
        else:
            lst[i], lst[j] = lst[j], lst[i]
    lst[pivot], lst[j] = lst[j], lst[pivot]

    return j

def quick_sort(lst):
    start, end = 0, len(lst) - 1
    while start < end:
        p = partition(lst)
        quick_sort(lst[:p])
        quick_sort(lst[p:])


class MinHeap:
    def __init__(self):
        self.min_heap = []

    def push(self, val):
        self.min_heap.append(val)
        self.percolate_up(len(self.min_heap) - 1)

    def percolate_up(self, i):
        parent_i = (i - 1) // 2
        if parent_i >= 0 and self.min_heap[i] < self.min_heap[parent_i]:
            self.min_heap[i], self.min_heap[parent_i] = self.min_heap[parent_i], self.min_heap[i]
            self.percolate_up(parent_i)

    def pop(self):
        if len(self.min_heap) == 0:
            return None
        if len(self.min_heap) == 1:
            return self.min_heap.pop()
        min_val = self.min_heap[0]
        self.min_heap[0] = self.min_heap.pop()
        self.percolate_down(0)
        return min_val

    def percolate_down(self, i):
        left_child = 2 * i + 1
        right_child = 2 * i + 2
        smallest = i

        if left_child < len(self.min_heap) and self.min_heap[left_child] < self.min_heap[smallest]:
            smallest = left_child
        if right_child < len(self.min_heap) and self.min_heap[right_child] < self.min_heap[smallest]:
            smallest = right_child
        if smallest != i:
            self.min_heap[i], self.min_heap[smallest] = self.min_heap[smallest], self.min_heap[i]
            self.percolate_down(smallest)

    def heapify(self):
        for i in range((len(self.min_heap) // 2) - 1, -1, -1):
            self.percolate_down(i)

    def peek(self):
        return self.min_heap[0] if self.min_heap else None