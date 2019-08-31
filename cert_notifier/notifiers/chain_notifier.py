# A virtual notifier that chains multiple notifiers
class ChainNotifier:
    def __init__(self, *notifiers):
        self.notifiers = []
        self.append(*notifiers)

    def send(self, msg):
        for n in self.notifiers:
            n.send(msg)

    def append(self, *notifiers):
        self.notifiers.extend(notifiers)
