import abc
import asyncio
from healthchecker.checker import CheckCase


class AsyncCheckCase(CheckCase):
    @property
    @abc.abstractproperty
    def loop(self):
        raise NotImplementedError

    async def _run_check(self, check):
        name, method = check
        try:
            return name, await method()
        except:
            return name, False

    def aggregated_checks(self):
        """
        Returns a future aggregating the parallel task execution os the
        check cases
        """
        tasks = (self._run_check(check)
                 for check in self._get_check_methods())
        return asyncio.gather(*tasks, return_exceptions=False)

    async def check(self):
        results = await self.aggregated_checks()
        self.check_report = {method_name: result
                             for method_name, result in results}

        return self.has_succeeded()
