"""Programming works: sorting algorithms that record every step.

Each algorithm is written the normal way, but it also logs "frames"
(the array plus what is being compared or swapped) so the web page can
replay the sort step by step, like the lecture slides.
"""

SORT_ORDER = ["bubble", "selection", "insertion", "merge", "quick"]

# Content taken from the Sorting Algorithms lecture.
SORT_INFO = {
    "bubble": {
        "name": "Bubble Sort",
        "definition": ("A simple comparison-based algorithm. Each pair of adjacent elements is compared "
                       "and swapped if they are not in order. The passes repeat until no swaps are needed."),
        "best_for": ["Small datasets", "Educational purposes to teach the concept of sorting"],
        "best_time": "O(n)", "avg_time": "O(n²)", "worst_time": "O(n²)", "space": "O(1)",
        "moves_label": "Swaps",
    },
    "selection": {
        "name": "Selection Sort",
        "definition": ("The list is split into a sorted part on the left and an unsorted part on the right. "
                       "The smallest element of the unsorted part is swapped with the leftmost unsorted element."),
        "best_for": ["Not recommended for large datasets",
                     "Memory space is limited (needs very little extra space)",
                     "Minimizing the number of swaps is a priority"],
        "best_time": "O(n²)", "avg_time": "O(n²)", "worst_time": "O(n²)", "space": "O(1)",
        "moves_label": "Swaps",
    },
    "insertion": {
        "name": "Insertion Sort",
        "definition": ("Builds the final sorted list one item at a time. Each element is taken from the input, "
                       "the spot where it belongs in the sorted part is found, and it is inserted there."),
        "best_for": ["The list is mostly sorted (only a few elements are misplaced)",
                     "The list is small", "Low memory usage is a priority"],
        "best_time": "O(n)", "avg_time": "O(n²)", "worst_time": "O(n²)", "space": "O(1)",
        "moves_label": "Swaps",
    },
    "merge": {
        "name": "Merge Sort",
        "definition": ("A divide-and-conquer algorithm. It splits the array into two halves, sorts each half "
                       "recursively, then merges the two sorted halves. A single element is already sorted."),
        "best_for": ["Large datasets", "Situations where a stable sort is needed",
                     "Enough memory is available (merging needs extra space)"],
        "best_time": "O(n log n)", "avg_time": "O(n log n)", "worst_time": "O(n log n)", "space": "O(n)",
        "moves_label": "Writes",
    },
    "quick": {
        "name": "Quick Sort",
        "definition": ("A divide-and-conquer algorithm invented by C.A.R. Hoare in 1960. It picks a pivot, "
                       "partitions the other elements into smaller and larger groups, then sorts each group."),
        "best_for": ["Average expected time of O(n log n)",
                     "Space efficiency matters (can be done in place with little extra memory)"],
        "best_time": "O(n log n)", "avg_time": "O(n log n)", "worst_time": "O(n²)", "space": "O(log n)",
        "moves_label": "Swaps",
    },
}

MAX_ITEMS = 12
MAX_ABS = 999


class Recorder:
    def __init__(self, values):
        self.a = list(values)
        self.frames = []
        self.sorted = set()
        self.comparisons = 0
        self.moves = 0

    def frame(self, msg, cmp=(), swap=(), mark=None, rng=None):
        self.frames.append({
            "a": list(self.a), "cmp": list(cmp), "swap": list(swap), "mark": mark,
            "range": list(rng) if rng else None, "sorted": sorted(self.sorted),
            "msg": msg, "c": self.comparisons, "s": self.moves,
        })

    def compare(self, i, j, msg, mark=None, rng=None):
        self.comparisons += 1
        self.frame(msg, cmp=(i, j), mark=mark, rng=rng)

    def swap(self, i, j, msg, mark=None, rng=None):
        self.a[i], self.a[j] = self.a[j], self.a[i]
        self.moves += 1
        self.frame(msg, swap=(i, j), mark=mark, rng=rng)

    def finish(self):
        self.sorted = set(range(len(self.a)))
        self.frame("Done! The list is sorted.")


def bubble_sort(values):
    r = Recorder(values)
    a, n = r.a, len(values)
    r.frame("Start. Compare each pair of neighbours.")
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            r.compare(j, j + 1, f"Is {a[j]} greater than {a[j + 1]}?")
            if a[j] > a[j + 1]:
                x, y = a[j], a[j + 1]
                r.swap(j, j + 1, f"Yes, so swap {x} and {y}.")
                swapped = True
        r.sorted.add(n - 1 - i)
        r.frame(f"{a[n - 1 - i]} has bubbled up to its final place.")
        if not swapped:
            r.frame("No swaps in that pass, so the list is already sorted.")
            break
    r.finish()
    return r


def selection_sort(values):
    r = Recorder(values)
    a, n = r.a, len(values)
    r.frame("Start. Find the lowest value, then place it first.")
    for i in range(n - 1):
        low = i
        r.frame(f"Pass {i + 1}: assume {a[low]} is the lowest so far.", mark=low)
        for j in range(i + 1, n):
            r.compare(j, low, f"Is {a[j]} lower than {a[low]}?", mark=low)
            if a[j] < a[low]:
                low = j
                r.frame(f"New lowest value: {a[low]}.", mark=low)
        if low != i:
            x, y = a[i], a[low]
            r.swap(i, low, f"Swap the lowest value {y} with the first unordered element {x}.")
        else:
            r.frame(f"{a[i]} is already in the right place.")
        r.sorted.add(i)
        r.frame(f"{a[i]} is now sorted.")
    r.finish()
    return r


def insertion_sort(values):
    r = Recorder(values)
    a, n = r.a, len(values)
    r.sorted = {0}
    r.frame("Start. The first element alone is a sorted list.")
    for i in range(1, n):
        r.sorted = set(range(i))
        pos = i
        r.frame(f"Take {a[pos]} and find where it belongs in the sorted part.", mark=pos)
        while pos > 0:
            r.compare(pos - 1, pos, f"Is {a[pos - 1]} greater than {a[pos]}?")
            if a[pos - 1] > a[pos]:
                x, y = a[pos - 1], a[pos]
                r.swap(pos - 1, pos, f"Yes, so move {y} one step left (past {x}).", mark=pos - 1)
                pos -= 1
            else:
                break
        r.sorted = set(range(i + 1))
        r.frame(f"{a[pos]} is inserted. The sorted part now has {i + 1} items.")
    r.finish()
    return r


def merge_sort(values):
    r = Recorder(values)
    n = len(values)
    r.frame("Start. Keep splitting in half, then merge the sorted halves.")

    def sort(lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        r.frame(f"Divide positions {lo} to {hi} into two halves.", rng=(lo, hi))
        sort(lo, mid)
        sort(mid + 1, hi)
        left, right = r.a[lo:mid + 1], r.a[mid + 1:hi + 1]
        r.frame(f"Merge {left} and {right}.", rng=(lo, hi))
        i = j = 0
        merged = []

        def place(val, msg):
            merged.append(val)
            r.moves += 1
            # show merged items first, then whatever is still waiting in each half
            r.a[lo:hi + 1] = merged + left[i:] + right[j:]
            r.frame(msg, swap=(lo + len(merged) - 1,), rng=(lo, hi))

        while i < len(left) and j < len(right):
            r.comparisons += 1
            if left[i] <= right[j]:
                val = left[i]
                msg = f"{left[i]} ≤ {right[j]}, so take {val} from the left half."
                i += 1
            else:
                val = right[j]
                msg = f"{left[i]} > {right[j]}, so take {val} from the right half."
                j += 1
            place(val, msg)
        while i < len(left):
            val = left[i]
            i += 1
            place(val, f"Copy the leftover {val}.")
        while j < len(right):
            val = right[j]
            j += 1
            place(val, f"Copy the leftover {val}.")
        r.sorted.update(range(lo, hi + 1))
        r.frame(f"Positions {lo} to {hi} are merged and sorted.", rng=(lo, hi))

    sort(0, n - 1)
    r.finish()
    return r


def quick_sort(values):
    r = Recorder(values)
    a, n = r.a, len(values)
    r.frame("Start. Pick a pivot, then split the rest around it.")

    def sort(lo, hi):
        if lo > hi:
            return
        if lo == hi:
            r.sorted.add(lo)
            r.frame(f"{a[lo]} is alone, so it is in its final place.", rng=(lo, hi))
            return
        pivot = a[hi]
        r.frame(f"Pick {pivot} (the last item) as the pivot.", mark=hi, rng=(lo, hi))
        i = lo - 1
        for j in range(lo, hi):
            r.compare(j, hi, f"Is {a[j]} less than the pivot {pivot}?", mark=hi, rng=(lo, hi))
            if a[j] < pivot:
                i += 1
                if i != j:
                    x, y = a[i], a[j]
                    r.swap(i, j, f"Swap {x} and {y} to keep smaller values on the left.", mark=hi, rng=(lo, hi))
        i += 1
        if i != hi:
            x = a[i]
            r.swap(i, hi, f"Put the pivot {pivot} between the groups (swap with {x}).", mark=i, rng=(lo, hi))
        r.sorted.add(i)
        r.frame(f"Pivot {pivot} is now in its final place (position {i}).", mark=i, rng=(lo, hi))
        sort(lo, i - 1)
        sort(i + 1, hi)

    sort(0, n - 1)
    r.finish()
    return r


ALGORITHMS = {
    "bubble": bubble_sort, "selection": selection_sort, "insertion": insertion_sort,
    "merge": merge_sort, "quick": quick_sort,
}


def validate(values):
    if not isinstance(values, list) or not (2 <= len(values) <= MAX_ITEMS):
        raise ValueError(f"Enter between 2 and {MAX_ITEMS} numbers.")
    clean = []
    for v in values:
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError("Use whole numbers only.")
        if abs(v) > MAX_ABS:
            raise ValueError(f"Keep each number between -{MAX_ABS} and {MAX_ABS}.")
        clean.append(v)
    return clean


def run_sort(algorithm, values):
    if algorithm not in ALGORITHMS:
        raise ValueError("Unknown sorting algorithm.")
    values = validate(values)
    r = ALGORITHMS[algorithm](values)
    return {"algorithm": algorithm, "frames": r.frames, "comparisons": r.comparisons,
            "moves": r.moves, "moves_label": SORT_INFO[algorithm]["moves_label"], "result": r.a}
