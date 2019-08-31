from .chain_notifier import ChainNotifier
from .console_notifier import ConsoleNotifier
from .debug_notifier import DebugNotifier
from .telegram_notifier import TelegramNotifier

notifier_map = dict(
    telegram=TelegramNotifier,
    console=ConsoleNotifier,
    debug=DebugNotifier
)

def get_notifiers(config):
    return ChainNotifier(*[
        v(**config[k])
        for k, v in notifier_map.items()
        if config.has_section(k) and config[k].getboolean('enable')
    ])
