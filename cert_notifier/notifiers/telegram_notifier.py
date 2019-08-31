import requests

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
