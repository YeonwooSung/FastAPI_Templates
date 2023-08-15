from fastapi import FastAPI


class Subject:
    def __init__(self):
        self.observers = []

    def register_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

class Resource(Subject):
    def __init__(self):
        super().__init__()
        self.data = []

    def add_data(self, new_data):
        self.data.append(new_data)
        self.notify_observers(new_data)

class Subscriber:
    def __init__(self, name):
        self.name = name

    def update(self, message):
        print(f"{self.name} received message: {message}")


app = FastAPI()
resource = Resource()


@app.post("/add_data/{new_data}")
def add_data(new_data: str):
    resource.add_data(new_data)
    return {"message": "Data added."}

@app.post("/subscribe/{subscriber_name}")
def subscribe(subscriber_name: str):
    subscriber = Subscriber(subscriber_name)
    resource.register_observer(subscriber)
    return {"message": f"{subscriber_name} subscribed."}

@app.post("/unsubscribe/{subscriber_name}")
def unsubscribe(subscriber_name: str):
    subscriber = Subscriber(subscriber_name)
    resource.remove_observer(subscriber)
    return {"message": f"{subscriber_name} unsubscribed."}
