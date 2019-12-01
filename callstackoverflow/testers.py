import logging
import docker
import dill
import base64
import pickle

logger = logging.getLogger(__name__)


class LocalTester:
    def test(self, fn, test):
        logger.debug("Lauching local tester %s on built fonction", test)
        try:
            return test(fn)
        except Exception as exc:
            logger.debug("Tests failed: %s", exc)
            return False
        logger.debug("Tests passed! Code is considered valid")
        return True


DOCKER_TEST_IMAGE = "cso-tester"

DOCKER_RUN_ARGS = {
    "auto_remove": True,
    "user": 65534,
    "network_disabled": True,
    "cpu_period": 100000,
    "cpu_quota": 50000,  # 0.5 cpu
    "mem_limit": "256m",  # 256Mo memory
    "environment": {"TEST_TIMEOUT": 5}
}


class DockerTester:
    def __init__(
            self, image=DOCKER_TEST_IMAGE, client_args={}, run_args={}):
        self._client = docker.DockerClient(**client_args)
        self._image = image
        self._run_args = DOCKER_RUN_ARGS.copy()
        self._run_args.update(run_args)

    def test(self, fn, test):
        try:
            fn_serialized = base64.b64encode(
                dill.dumps(fn, byref=False, recurse=True)).decode()
            test_serialized = base64.b64encode(
                dill.dumps(test, byref=False, recurse=True)).decode()
        except pickle.PicklingError as err:
            logger.warning("Failed to pickle function: {}".format(err))
            return False

        try:
            self._client.containers.run(
                self._image, [fn_serialized, test_serialized],
                **self._run_args)
        except docker.errors.ContainerError:
            return False
        return True
