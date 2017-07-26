import logging

logger = logging.getLogger(__name__)


def apply_tests(func, tester):
    logger.info("Lauching tester %s on built fonction", tester)
    if tester is None:
        logger.warning("Validating function with None tester")
        return True

    try:
        tester(func)
    except Exception as exc:
        logger.debug("Tests failed: %s", exc)
        return False
    logger.info("Tests passed! Code is considered valid")
    return True
