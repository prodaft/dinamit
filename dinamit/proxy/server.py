from twisted.names import dns
from twisted.names import server
from dinamit import RUN_DIR, GLOBAL_SETTINGS
from dinamit.core.constants import DomainAction
from dinamit.core.models import db
from dinamit.core.utils import create_rule_hash
from pony.orm import db_session
import tldextract
import os

extractor = tldextract.TLDExtract(cache_file=os.path.join(RUN_DIR, 'tld.cache'))


class DNSProxyServer(server.DNSServerFactory):

    @db_session
    def handleQuery(self, message, proto, address=None):
        client_ip, _ = address
        query = message.queries[0]
        raw_query = str(query.name)

        asset = db.Asset.select(lambda a: a.ip == client_ip and a.is_verified).first()
        if GLOBAL_SETTINGS['internal']:
            client = db.Client.select().first()
        else:
            if not asset:
                return self.returnAnswer(raw_query, message, proto, address)
            client = asset.client

        policy = client.policy
        query_type = dns.QUERY_TYPES.get(query.type, dns.EXT_QUERIES.get(query.type, 'UNKNOWN {}'.format(query.type)))
        extracted = extractor(raw_query).registered_domain
        is_subdomain = extracted != raw_query
        domain = db.Domain.select(lambda d: d.name == extracted).first()
        if not domain and is_subdomain:
            domain = db.Domain.select(lambda d: d.name == raw_query).first()
        elif domain and not domain.is_subdomain:
            pass
        else:
            domain = None

        rh = create_rule_hash(client_ip, raw_query)

        refused = False
        reason = 'UNCATEGORIZED'
        if rh in client.rules and client.rules[rh]['action'] == 'DENY':
            refused = True
            reason = 'RULE'

        allowed_categories = policy.get('ALLOWED_CATEGORIES', [])
        if domain and domain.category not in allowed_categories:
            refused = True
            reason = domain.category.name

        action = DomainAction.DENY if refused else DomainAction.ALLOW
        client.queries.create(
            request=raw_query, dns_type=query_type, action=action, reason=reason, asset=asset, domain=domain
        )

        if refused:
            return self.returnAnswer(raw_query, message, proto, address)
        return server.DNSServerFactory.handleQuery(self, message, proto, address)

    def returnAnswer(self, name, message, proto, address):
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_A(address=GLOBAL_SETTINGS['proxy']['landpage_ip']),
            ttl=GLOBAL_SETTINGS['proxy']['blocked_ttl']
        )
        answers = [answer]
        authority = []
        additional = []
        response = self._responseFromMessage(
            message=message, rCode=dns.OK,
            answers=answers, authority=authority, additional=additional
        )
        self.sendReply(proto, response, address)

    def returnRefused(self, message, proto, address):
        message.rCode = dns.EREFUSED
        self.sendReply(proto, message, address)

    def gotResolverResponse(self, resp, proto, message, address):
        return server.DNSServerFactory.gotResolverResponse(self, resp, proto, message, address)

    def gotResolverError(self, failure, proto, message, address):
        return server.DNSServerFactory.gotResolverError(self, failure, proto, message, address)
