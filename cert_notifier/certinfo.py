from datetime import datetime
from ssl import cert_time_to_seconds

# Class for parsing certificate information
class CertInfo:
    # certinfo: SSLSocket.getpeercert()
    # cert: SSLSocket.getpeercert(True)
    def __init__(self, certinfo, cert=None):
        self.cert = cert
        self.certinfo = certinfo

        # Certificate common name
        self.subject = dict(x[0] for x in self.certinfo['subject'])

        # Issuer common name
        self.issuer = dict(x[0] for x in self.certinfo['issuer'])

        # Expire time
        self.notBefore = datetime.utcfromtimestamp(cert_time_to_seconds(self.certinfo['notBefore']))
        self.notAfter = datetime.utcfromtimestamp(cert_time_to_seconds(self.certinfo['notAfter']))

    # Certificate time calculations
    @property
    def duration(self):
        return self.notAfter - self.notBefore

    @property
    def elapsed(self):
        return datetime.utcnow() - self.notBefore

    @property
    def remain(self):
        return self.notAfter - datetime.utcnow()

    @property
    def percent(self):
        return self.elapsed / self.duration

    @property
    def key(self):
        return self.subject['commonName'], self.notBefore.timestamp(), self.notAfter.timestamp()
