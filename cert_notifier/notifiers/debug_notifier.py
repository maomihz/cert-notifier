# Print all arguments passed to the notifier, and do nothing
class DebugNotifier:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def send(self, msg):
        print(self.kwargs)

