#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl
import socket
from ssl import cert_time_to_seconds
from datetime import datetime, timezone, timedelta
import configparser


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



def run():
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read('config.conf')

    config = parser['main']
    hosts = parser['hosts']

    # define the format of text
    # error: ssl host error
    # warn: certificate close to expiry
    # ok: host ok with certificate issuer
    # ok2: host ok but hide certificate issuer
    text = dict(
        error='❌ {host} \n{reason}\n',
        warn ='⚠️ [{days}天{hours:2d}小时] {issued_by}\n{hosts}\n',
        ok   ='✅ [{days}天] {issued_by}\n{hosts}\n'
    )


    # <connect> to all defined hosts and obtain certificate info
    hosts = [SSLHost(a, refresh=True) for a in hosts]

    # Group hosts by certificate
    certs = dict()
    errors = list()
    for h in hosts:
        if h.error():
            errors.append(h)
            continue
        certinfo = h.certinfo
        key = certinfo.key
        if key in certs:
            certs[key][1].append(h.host)
        else:
            certs[key] = certinfo, [h.host]
        # print(certs)



    has_ok = False
    has_error = bool(errors)
    has_warn = False

    info = []
    for h in errors:
        info.append(text['error'].format(
            host = h.host,
            reason = h.reason,
        ))

    for cert, hosts in sorted(certs.values(), key=lambda v : v[0].remain):
        # set the type of message
        msg_type = 'ok'
        if cert.remain.days <= config.getint('warn_days'):
            msg_type = 'warn'
            has_warn = True

        # format the text
        info.append(text[msg_type].format(
            hosts = '\n'.join(hosts),
            days = cert.remain.days,
            hours = cert.remain.seconds // 3600,
            issued_by = cert.issuer['commonName']
        ))


    # Obtain notifiers and send notifications
    from notifier import get_notifiers
    notifier = get_notifiers(parser)

    msg = '\n'.join(info)
    if config.getboolean('notify_ok') or (config.getboolean('notify_error') and has_error) or (config.getboolean('notify_warn') and has_warn):
        return notifier.send('当前时间：{}\n{}'.format(
            datetime.now().strftime('%F %T'),
            msg
        ))

    return msg

if __name__ == '__main__':
    result = run()
    # try:
    #     value = json.loads(result)
    # except json.decoder.JSONDecodeError:
    #     print(result)
    #     exit(0)

    # print(value)
    # if value['ok']:
    #     msgid = value['result']['message_id']
    # try:
    #     with open('last_id', 'r') as f:
    #         last_id = int(f.read())
    #         telegram_delete(last_id)
    # except FileNotFoundError:
    #     pass
    # except ValueError:
    #     pass
    # with open('last_id', 'w') as f:
    #     f.write(str(msgid))
