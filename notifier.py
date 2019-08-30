import requests


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




# Print all arguments passed to the notifier, and do nothing
class DebugNotifier:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def send(self, msg):
        print(self.kwargs)


# Print the message to console
class ConsoleNotifier:
    def __init__(self, **kwargs):
        pass
    def send(self, msg):
        print(msg)


# Send a message to a telegram chat
class TelegramNotifier:
    def __init__(self, token, chat, **kwargs):
        self.token = token
        self.chat = chat

    def _tg_url(self, method=''):
        return 'https://api.telegram.org/bot%s/%s' % (self.token, method)

    # Send a message to a chat
    def send(self, msg):
        if not msg:
            return None
        return requests.get(self._tg_url('sendMessage'),
                params = dict(
                    chat_id=self.chat,
                    text=msg,
                    parse_mode='HTML')).text

    # Delete a message
    def delete(self, id):
        if not id:
            return None
        return requests.get(self._tg_url('deleteMessage'),
                params = dict(
                    chat_id=chat,
                    message_id=id)).text




notifier_map = dict(
    telegram=TelegramNotifier,
    console=ConsoleNotifier,
    debug=DebugNotifier
)

def get_notifiers(config):
    notifier = ChainNotifier()
    for k, v in notifier_map.items():
        if config.has_section(k) and config[k].getboolean('enable'):
            notifier.append(v(**config[k]))
    return notifier
