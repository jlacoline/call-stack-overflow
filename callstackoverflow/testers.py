import logging

logger = logging.getLogger(__name__)


def apply_tests(func, tester):
    logger.debug("Lauching tester %s on built fonction", tester)
    try:
        return tester(func)
    except Exception as exc:
        logger.debug("Tests failed: %s", exc)
        return False
    logger.debug("Tests passed! Code is considered valid")
    return True
