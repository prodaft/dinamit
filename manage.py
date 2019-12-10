import argparse
import sys
from getpass import getpass
from dinamit import GLOBAL_SETTINGS
from dinamit.panel.app import app as panelapp
from dinamit.panel.app import bcrypt
from dinamit.landpage.app import app as landapp
from dinamit.core.models import db, EnumConverter
from dinamit.panel.helpers import create_super_user
from dinamit.proxy.server import DNSProxyServer
from dinamit.tasks import celery
from pony.flask import Pony
from pony.orm import db_session
from pony.orm.dbapiprovider import OperationalError
from twisted.internet import reactor
from twisted.names import client, dns
from twisted.python import log
from codecs import decode
from enum import Enum

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'dinamit', description='Dinamit'
    )

    parser.add_argument(
        '--panel', help='Web panel', dest='panel',
        action='store_true', default=False
    )

    parser.add_argument(
        '--create-super-user', help='Create super user', dest='create_super_user',
        action='store_true', default=False
    )

    parser.add_argument(
        '--init-feed', help='Init feed database', dest='init_feed',
        action='store_true', default=False
    )

    parser.add_argument(
        '--worker', help='Worker', dest='worker',
        action='store_true', default=False
    )

    parser.add_argument(
        '--proxy', help='Proxy', dest='proxy',
        action='store_true', default=False
    )

    parser.add_argument(
        '--landpage', help='Landpage', dest='landpage',
        action='store_true', default=False
    )

    args = parser.parse_args()
    option_flag = False

    try:
        db.bind(**panelapp.config['PONY'])
        db.provider.converter_classes.append((Enum, EnumConverter))
        db.generate_mapping(create_tables=True)
    except OperationalError:
        print('[!] Database connection error happened. ')
        sys.exit(1)

    if args.create_super_user:
        option_flag = True
        email = input('Email: ').strip()
        password = getpass('Password: ').strip()
        first_name = input('First Name: ').strip()
        last_name = input('Last Name: ').strip()
        with db_session:
            created = create_super_user(
                email, decode(bcrypt.generate_password_hash(password), 'utf-8'), first_name, last_name
            )
        if created:
            print('[+] Super user created.')
        else:
            print('[-] Super user already exists.')

    if args.worker:
        option_flag = True
        argv = [
            'worker',
            '-E',
            '-B',
            '--loglevel={}'.format(GLOBAL_SETTINGS['broker']['log_level'])
        ]
        celery.worker_main(argv)

    if args.panel:
        option_flag = True
        Pony(panelapp)

        panelapp.run(
            host=GLOBAL_SETTINGS['panel']['host'],
            port=GLOBAL_SETTINGS['panel']['port'],
            debug=GLOBAL_SETTINGS['debug']
        )

    if args.landpage:
        option_flag = True
        Pony(landapp)

        landapp.run(
            host=GLOBAL_SETTINGS['landpage']['host'],
            port=GLOBAL_SETTINGS['landpage']['port'],
            debug=GLOBAL_SETTINGS['debug']
        )

    if args.proxy:
        option_flag = True
        log.startLogging(sys.stdout)
        resolver = client.Resolver(
            servers=[(server, 53) for server in GLOBAL_SETTINGS['proxy']['upstream']]
        )
        factory = DNSProxyServer(clients=[resolver], verbose=0)
        protocol = dns.DNSDatagramProtocol(factory)

        reactor.listenUDP(GLOBAL_SETTINGS['proxy']['listen']['port'], protocol)
        reactor.listenTCP(GLOBAL_SETTINGS['proxy']['listen']['port'], protocol)
        reactor.run()


    if not option_flag:
        parser.print_usage()
