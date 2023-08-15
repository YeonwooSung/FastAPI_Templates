from fastapi import FastAPI


class SortStrategy:
    def sort(self, data: list[int]) -> list[int]:
        pass

class BubbleSort(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        n = len(data)
        for i in range(n):
            for j in range(n-i-1):
                if data[j] > data[j+1]:
                    data[j], data[j+1] = data[j+1], data[j]
        return data

class QuickSort(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        if len(data) <= 1:
            return data
        pivot = data[len(data)//2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, data: list[int]) -> list[int]:
        return self.strategy.sort(data)


app = FastAPI()
sorter = Sorter(BubbleSort())


@app.post("/sort/{strategy}")
def sort_data(strategy: str, data: list[int]):
    if strategy == "bubble":
        sorter.set_strategy(BubbleSort())
    elif strategy == "quick":
        sorter.set_strategy(QuickSort())
    else:
        return {
            "message": "Invalid sorting strategy.",
            "sorted_data": []
        }
    sorted_data = sorter.sort(data)
    return {
        "message": f"{strategy} sort successful.",
        "sorted_data": sorted_data
    }
