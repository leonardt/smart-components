import pytest
from magma import clear_cachedFunctions
import magma
import logging

collect_ignore = ["src"]  # pip folder that contains dependencies like magma


@pytest.fixture(autouse=True)
def magma_test():
    magma.util.reset_global_context()
    logging.getLogger().setLevel(logging.DEBUG)
