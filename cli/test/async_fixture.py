import logging
import sys
from statistics import mean
import time
import asyncio
from pprint import pformat
from typing import Any, Optional
from dataclasses import dataclass, field
from asyncio import create_task, run
from test_utils import get_secret
from mobilecoin import AsyncClient, pmob2mob

sender_acct = get_secret("SENDER_ACCOUNT")
receiver_address = get_secret("RECEIVER_ADDRESS")

@dataclass
class FullServiceHelper:
    """
    Async test fixture class. Methods with 'test_' are isolated tests
    meant to run until event loop completion so that they can be run
    in CI/CD. A new instance should be made for each test.
    Attributes:
      results (dict): Container of individual test results to be evaluated by a
      test framework
      stats (dict): Pretty formatted summary of test statistics
    """
    def __init__(self) -> None:
        self.client = AsyncClient()

    test_name: str = ""
    start_time: float = 0.0
    results: dict[str, Any] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)

    async def confirm_tx_success(self,
            tx_log_id: str,
            start: float,
            timeout: int = 30,
        ) -> None:
        """
        Confirm transaction success
        """
        confirmation_start = time.time()
        status = ""
        result = {}
        for i in range(timeout):
            result = await self.client.get_transaction_log(tx_log_id)
            status = result.get("status")
            if status == "tx_status_succeeded":
                break
            await asyncio.sleep(0.5)
        logging.info("tx_result %s", status)
        _id = "tx_send_{tx_log_id}_at_{start}"
        params = {"confirmation_time": time.time() - confirmation_start}
        self.log_result(_id,status == "tx_status_succeeded", result, start, params) 

    async def send_n_txs(
        self, outputs: list[list[tuple[str, int]]], interval: float = 1, **params: Any
    ) -> None:
        """
        Send N transactions asynchronously
        
        args:
          output_list: list of address_and_value pairs to sent in a tx
        """
        logging.info("sending %s txs in %s secs", len(outputs), len(outputs) * wait)
        tasks: list[asyncio.Task] = []
        for output in outputs:
            await asyncio.sleep(interval)
            tasks += [create_task(self.send_tx(output, **params))]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def create_n_addresses(self, number: int, interval: float) -> dict:
        """
        Create N accounts asynchronously
        
        args:
            number (int): number of accounts to create
            interval (float): interval between creation
        """
        logging.info("creating %s accounts at a %s s interval",amount, interval)
        prefix = "address"
        tasks = []
        for i in range(n):
            await asyncio.sleep(interval)
            tasks += [create_task(self.create_address())]
        await asyncio.gather(**tasks, return_exceptions=True)

    async def create_address():
        start = time.time()
        name = f"address{str(i)}"
        _id = "create_{name}_at_{start}"
        try:
            address = await self.client.assign_address_for_account(sender_acct, name)
            self.log_result(_id, True, address, start) 
        except Exception as e:
            self.log(_id, False, e, start)

    def log_result(self,
        _id: "str", 
        _pass: bool, 
        data: Optional[dict], 
        start: float,
        **params,
    ) -> None:
        self.results[_id] = {
            "test": self.test_name,
            "pass": _pass,
            "data": result,
            "runtime": time.time() - start,
            **params,
        }

    async def send_tx(
            self, amount: Union[int, float], 
            to_address: str, 
            confirm: bool = False,
    ) -> None:
        """
        Send a transaction and store its success/failure
        """
        start = time.time()
        try:
            log_id = await self.client.build_and_submit_transaction(
                    account_id=sender_acct,
                    amount=amount,
                    to_address=to_address,
                )
        except Exception as e:
            _id = f"send-{amount}-to-{to_address}-at-{start}"
            self.log_result(_id, e, False, start)

        await self.confirm_tx_success(tx_log_id, start)

    def summarize(self) -> None:
        tests = self.results.values()
        num_pass = len([True for test in tests if test["pass"]])
        self.stats = {
            "name": self.test_name,
            "test_runtime": time.time() - self.start_time,
            "num_pass": num_pass,
            "fail": len(tests) - num_pass,
            "step_runtime_avg": mean([test["runtime"] for test in tests]),
        }
        logging.info("test summary:\n %s", pformat(self.stats))


@dataclass
class FullServiceTester(FullServiceHelper):

    ### Individual tests to run in a testing framework (pytest,etc..)

    async def test_concurrent_build_then_submit(
        self, num: int, amt: float, wait: float = 0.1
    ) -> dict[str, Any]:
        self.test_name = sys._getframe(0).f_code.co_name
        self.start_time = time.time()
        await self.send_n_txs([[(receiver_address, pmob(amt))]] * num, wait)
        self.summarize()
        return self.results

    async def test_concurrent_build_and_submit(
        self, num: int, amt: float, wait: float = 0.1, submit: bool = True
    ) -> dict[str, Any]:
        self.start_time = time.time()
        self.test_name = sys._getframe(0).f_code.co_name
        await self.send_n_txs(
            [[(receiver_address, pmob(amt))]] * num, wait, submit=submit
        )
        self.summarize()
        return self.results


fst = FullServiceTester()

if __name__ == "__main__":
    run(fst.test_concurrent_build_and_submit(25, 0.001, 0.1)),
