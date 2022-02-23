#type: ignore
from decimal import Decimal
import json
import asyncio
import uuid
import aiohttp

DEFAULT_URL = 'http://127.0.0.1:9090/wallet'

MAX_TOMBSTONE_BLOCKS = 100


class WalletAPIError(Exception):
    def __init__(self, response):
        self.response = response
        super().__init__()


class AsyncClient:

    def __init__(self, url=None, verbose=False):
        if url is None:
            url = DEFAULT_URL
        self.url = url
        self.verbose = verbose
        self._query_count = 0

    async def _req(self, request_data):
        default_params = {
            "jsonrpc": "2.0",
            "api_version": "2",
            "id": uuid.uuid4().hex,
        }

        request_data = {**request_data, **default_params}

        if self.verbose:
            print('POST', self.url)
            print(json.dumps(request_data, indent=2))
            print()

        try:
            async with aiohttp.TCPConnector() as conn:
                async with aiohttp.ClientSession(connector=conn) as sess:
                    _req = sess.post(
                        self.url,
                        data=json.dumps(request_data),
                        headers={"Content-Type": "application/json"},
                    )
                    async with _req as resp:
                        response_data = await resp.json()
        except aiohttp.ClientConnectionError as e:
            err = f"Could not connect to wallet server at {self.url}"
            raise aiohttp.ClientConnectionError(err) from e
        except aiohttp.client.ContentTypeError as e:
            raise ValueError(f"API returned invalid JSON: {_req}") from e

        if self.verbose:
            print(resp.status, resp.reason)
            print(json.dumps(response_data, indent=2))
            print()

        # Check for errors and unwrap result.
        if 'result' not in response_data:
            raise WalletAPIError(response_data)

        self._query_count += 1
        return response_data['result']

    async def create_account(self, name=None):
        r = await self._req({
            "method": "create_account",
            "params": {
                "name": name,
            }
        })
        return r['account']

    async def import_account(self, mnemonic, key_derivation_version=2, name=None, first_block_index=None, next_subaddress_index=None, fog_keys=None):
        params = {
            'mnemonic': mnemonic,
            'key_derivation_version': str(int(key_derivation_version)),
        }
        if name is not None:
            params['name'] = name
        if first_block_index is not None:
            params['first_block_index'] = str(int(first_block_index))
        if next_subaddress_index is not None:
            params['next_subaddress_index'] = str(int(next_subaddress_index))
        if fog_keys is not None:
            params.update(fog_keys)

        r = await self._req({
            "method": "import_account",
            "params": params
        })
        return r['account']

    async def import_account_from_legacy_root_entropy(self, legacy_root_entropy, name=None, first_block_index=None, next_subaddress_index=None, fog_keys=None):
        params = {
            'entropy': legacy_root_entropy,
        }
        if name is not None:
            params['name'] = name
        if first_block_index is not None:
            params['first_block_index'] = str(int(first_block_index))
        if next_subaddress_index is not None:
            params['next_subaddress_index'] = str(int(next_subaddress_index))
        if fog_keys is not None:
            params.update(fog_keys)

        r = await self._req({
            "method": "import_account_from_legacy_root_entropy",
            "params": params
        })
        return r['account']

    async def get_all_accounts(self):
        r = await self._req({"method": "get_all_accounts"})
        return r['account_map']

    async def get_account(self, account_id):
        r = await self._req({
            "method": "get_account",
            "params": {"account_id": account_id}
        })
        return r['account']

    async def update_account_name(self, account_id, name):
        r = await self._req({
            "method": "update_account_name",
            "params": {
                "account_id": account_id,
                "name": name,
            }
        })
        return r['account']

    async def remove_account(self, account_id):
        return await self._req({
            "method": "remove_account",
            "params": {"account_id": account_id}
        })

    async def export_account_secrets(self, account_id):
        r = await self._req({
            "method": "export_account_secrets",
            "params": {"account_id": account_id}
        })
        return r['account_secrets']

    async def get_all_txos_for_account(self, account_id):
        r = await self._req({
            "method": "get_all_txos_for_account",
            "params": {"account_id": account_id}
        })
        return r['txo_map']

    async def get_txo(self, txo_id):
        r = await self._req({
            "method": "get_txo",
            "params": {
                "txo_id": txo_id,
            },
        })
        return r['txo']

    async def get_network_status(self):
        r = await self._req({
            "method": "get_network_status",
        })
        return r['network_status']

    async def get_balance_for_account(self, account_id):
        r = await self._req({
            "method": "get_balance_for_account",
            "params": {
                "account_id": account_id,
            }
        })
        return r['balance']

    async def get_balance_for_address(self, address):
        r = await self._req({
            "method": "get_balance_for_address",
            "params": {
                "address": address,
            }
        })
        return r['balance']

    async def assign_address_for_account(self, account_id, metadata=None):
        if metadata is None:
            metadata = ''

        r = await self._req({
            "method": "assign_address_for_account",
            "params": {
                "account_id": account_id,
                "metadata": metadata,
            },
        })
        return r['address']

    async def get_addresses_for_account(self, account_id, offset=0, limit=1000):
        r = await self._req({
            "method": "get_addresses_for_account",
            "params": {
                "account_id": account_id,
                "offset": str(int(offset)),
                "limit": str(int(limit)),
            },
        })
        return r['address_map']

    async def _build_and_submit_transaction(self, account_id, amount, to_address, fee):
        amount = str(mob2pmob(amount))
        params = {
            "account_id": account_id,
            "addresses_and_values": [(to_address, amount)],
        }
        if fee is not None:
            params['fee'] = str(mob2pmob(fee))
        r = await self._req({
            "method": "build_and_submit_transaction",
            "params": params,
        })
        return r

    async def build_and_submit_transaction(self, account_id, amount, to_address, fee=None):
        r = await self._build_and_submit_transaction(account_id, amount, to_address, fee)
        return r['transaction_log']

    async def build_and_submit_transaction_with_proposal(self, account_id, amount, to_address, fee=None):
        r = await self._build_and_submit_transaction(account_id, amount, to_address, fee)
        return r['transaction_log'], r['tx_proposal']

    async def build_transaction(self, account_id, amount, to_address, tombstone_block=None, fee=None):
        amount = str(mob2pmob(amount))
        params = {
            "account_id": account_id,
            "addresses_and_values": [(to_address, amount)],
        }
        if tombstone_block is not None:
            params['tombstone_block'] = str(int(tombstone_block))
        if fee is not None:
            params['fee'] = str(mob2pmob(fee))
        r = await self._req({
            "method": "build_transaction",
            "params": params,
        })
        return r['tx_proposal']

    async def submit_transaction(self, tx_proposal, account_id=None):
        r = await self._req({
            "method": "submit_transaction",
            "params": {
                "tx_proposal": tx_proposal,
                "account_id": account_id,
            },
        })
        return r['transaction_log']

    async def get_all_transaction_logs_for_account(self, account_id):
        r = await self._req({
            "method": "get_all_transaction_logs_for_account",
            "params": {
                "account_id": account_id,
            },
        })
        return r['transaction_log_map']

    async def create_receiver_receipts(self, tx_proposal):
        r = await self._req({
            "method": "create_receiver_receipts",
            "params": {
                "tx_proposal": tx_proposal,
            },
        })
        return r['receiver_receipts']

    async def check_receiver_receipt_status(self, address, receipt):
        r = await self._req({
            "method": "check_receiver_receipt_status",
            "params": {
                "address": address,
                "receiver_receipt": receipt,
            }
        })
        return r

    async def build_gift_code(self, account_id, amount, memo=""):
        amount = str(mob2pmob(amount))
        r = await self._req({
            "method": "build_gift_code",
            "params": {
                "account_id": account_id,
                "value_pmob": amount,
                "memo": memo,
            },
        })
        return r

    async def submit_gift_code(self, gift_code_b58, tx_proposal, account_id):
        r = await self._req({
            "method": "submit_gift_code",
            "params": {
                "gift_code_b58": gift_code_b58,
                "tx_proposal": tx_proposal,
                "from_account_id": account_id,
            },
        })
        return r['gift_code']

    async def get_gift_code(self, gift_code_b58):
        r = await self._req({
            "method": "get_gift_code",
            "params": {
                "gift_code_b58": gift_code_b58,
            },
        })
        return r['gift_code']

    async def check_gift_code_status(self, gift_code_b58):
        r = await self._req({
            "method": "check_gift_code_status",
            "params": {
                "gift_code_b58": gift_code_b58,
            },
        })
        return r

    async def get_all_gift_codes(self):
        r = await self._req({
            "method": "get_all_gift_codes",
        })
        return r['gift_codes']

    async def claim_gift_code(self, account_id, gift_code_b58):
        r = await self._req({
            "method": "claim_gift_code",
            "params": {
                "account_id": account_id,
                "gift_code_b58": gift_code_b58,
            },
        })
        return r['txo_id']

    async def remove_gift_code(self, gift_code_b58):
        r = await self._req({
            "method": "remove_gift_code",
            "params": {
                "gift_code_b58": gift_code_b58,
            },
        })
        return r['removed']

    # Utility methods.

    async def poll_balance(self, account_id, min_block_height=None, seconds=10, poll_delay=1.0):
        for _ in range(seconds):
            balance = await self.get_balance_for_account(account_id)
            if balance['is_synced']:
                if (
                    min_block_height is None
                    or int(balance['account_block_height']) >= min_block_height
                ):
                    return balance
            await asyncio.sleep(poll_delay)
        else:
            raise Exception('Could not sync account {}'.format(account_id))

    async def poll_gift_code_status(self, gift_code_b58, target_status, seconds=10, poll_delay=1.0):
        for _ in range(seconds):
            response = await self.check_gift_code_status(gift_code_b58)
            if response['gift_code_status'] == target_status:
                return response
            await asyncio.sleep(poll_delay)
        else:
            raise Exception('Gift code {} never reached status {}.'.format(gift_code_b58, target_status))

    async def poll_txo(self, txo_id, seconds=10, poll_delay=1.0):
        for _ in range(10):
            try:
                return await self.get_txo(txo_id)
            except WalletAPIError:
                pass
            await asyncio.sleep(poll_delay)
        else:
            raise Exception('Txo {} never landed.'.format(txo_id))


PMOB = Decimal("1e12")


def mob2pmob(x):
    """Convert from MOB to picoMOB."""
    result = round(Decimal(x) * PMOB)
    assert 0 <= result < 2**64
    return result


def pmob2mob(x):
    """Convert from picoMOB to MOB."""
    result = int(x) / PMOB
    if result == 0:
        result = Decimal("0")
    return result
