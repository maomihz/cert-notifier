#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from datetime import datetime
from .sslhost import SSLHost
from .notifiers import get_notifiers

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



# Run a single instance of the program with the specified configuration file
def run_one(configfile):
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read(configfile)

    config = parser['main']
    if not config.getboolean('enable'):
        print('Skipping disabled configuration')
        return

    hosts = parser['hosts']



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
    notifier = get_notifiers(parser)

    msg = '\n'.join(info)
    if config.getboolean('notify_ok') or (config.getboolean('notify_error') and has_error) or (config.getboolean('notify_warn') and has_warn):
        return notifier.send('当前时间：{}\n{}'.format(
            datetime.now().strftime('%F %T'),
            msg
        ))

    return msg

import os
from os.path import join

def run(configdir="config"):
    # Search configuration file and run them all
    for dirpath, dirnames, filenames in os.walk(configdir):
        for fname in filter(lambda f : f.endswith('.conf'), filenames):
            path = join(dirpath, fname)
            print("Found configuration file", path)
            run_one(path)
