import asyncio
from contextlib import contextmanager
from decimal import Decimal
import sys
import tempfile
import time

from mobilecoin.async_client import (
    AsyncClient,
    WalletAPIError,
    pmob2mob,
)
from mobilecoin.cli import (
    CommandLineInterface,
    _load_import,
)


async def main():
    cli = _start_test_server()

    c = AsyncClient(verbose=True)

    account = await c.create_account()
    account_id = account['account_id']

    await create_subaddresses(c, account_id, num_addresses=10)

    print('ALL PASS')

    cli.stop()


def create_subaddresses(c, account_id, num_addresses):
    num_addresses = 10
    tasks = []
    for i in range(num_addresses):
        tasks.append(asyncio.create_task(c.assign_address_for_account(account_id, str(i))))
        await asyncio.sleep(0.000001)
    await asyncio.gather(*tasks, return_exceptions=True)

    await asyncio.sleep(1.0)
    addresses = await c.get_addresses_for_account(account_id)
    print(len(addresses))
    assert len(addresses) == num_addresses + 2, 'not enough addresses created'


def _start_test_server():
    # Create a test wallet database, and start the server.
    db_file = tempfile.NamedTemporaryFile(suffix='.db', prefix='test_wallet_', delete=False)
    cli = CommandLineInterface()
    cli.config['wallet-db'] = db_file.name
    cli.stop()
    time.sleep(0.5)  # Wait for other servers to stop.
    cli.start(bg=True, unencrypted=True)
    time.sleep(2.0)  # Wait for the server to start listening.
    return cli


if __name__ == '__main__':
    asyncio.run(main())
