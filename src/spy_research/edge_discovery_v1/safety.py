"""Explicit process-local offline guard, installed by the Phase 1 builder."""
import re
import sys
from datetime import date
from .inventory import role_for


def deny_network(*args, **kwargs):
    raise PermissionError('network/broker access prohibited')


def install_audit_guard():
    accessed = set()
    def guard(event, args):
        if event in ('socket.connect','socket.getaddrinfo','socket.sendto','socket.bind'):
            deny_network()
        if event == 'open' and isinstance(args[0],(str,bytes)) and str(args[0]).endswith('.parquet'):
            match = re.search(r'(\d{4}-\d{2}-\d{2})\.parquet$',str(args[0]))
            if not match: raise PermissionError('unrecognized market partition')
            role_for(date.fromisoformat(match[1]))
            accessed.add(str(args[0]))
    sys.addaudithook(guard)
    return accessed
