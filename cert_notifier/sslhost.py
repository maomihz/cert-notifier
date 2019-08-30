import ssl
import socket

from . import CertInfo

class SSLHost:
    def __init__(self, hostname, refresh=False):
        self.host = hostname
        self.reason = None # Reason for error

        if refresh:
            self.refresh()

    def error(self, reason=None):
        if reason:
            self.reason = reason
        return self.reason

    def refresh(self):
        try:
            # Create a socket and connect to it
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(socket.socket(), server_hostname=self.host)
            s.connect((self.host, 443))
        except ssl.SSLError as e:
            self.error(e.reason)
        except ConnectionRefusedError as e:
            self.error("Connection Refused")
        except socket.gaierror as e:
            self.error("Name Not Resolved")
        except Exception as e:
            self.error(str(e))


        if self.error():
            return

        try:
            self.certinfo = CertInfo(s.getpeercert(), s.getpeercert(True))
        except KeyError:
            self.error('Missing subjects in certificate.')


