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
        except ssl.SSLCertVerificationError as e:
            self.error("[%d] %s" % (e.verify_code, e.verify_message))
        except ssl.SSLError as e:
            # Generic error related to SSL connection
            self.error(e.reason)
        except ConnectionError as e:
            # Generic error related to TCP connection
            self.error(str(e))
        except socket.gaierror as e:
            # Host name resolution error
            self.error(str(e))
        except Exception as e:
            # Any other error
            self.error(str(e))


        if self.error():
            return

        try:
            self.certinfo = CertInfo(s.getpeercert(), s.getpeercert(True))
        except KeyError:
            self.error('Missing subjects in certificate.')


