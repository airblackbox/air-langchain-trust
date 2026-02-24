"""Shared test fixtures."""

import pytest
from air_langchain_trust import AirTrustCallbackHandler, AirTrustConfig, ConsentMode


@pytest.fixture
def config():
    return AirTrustConfig()


@pytest.fixture
def handler(config):
    return AirTrustCallbackHandler(config=config)


@pytest.fixture
def permissive_handler():
    return AirTrustCallbackHandler(config=AirTrustConfig(consent_mode=ConsentMode.ALLOW_ALL))


@pytest.fixture
def disabled_handler():
    return AirTrustCallbackHandler(config=AirTrustConfig(enabled=False))


@pytest.fixture
def strict_handler():
    return AirTrustCallbackHandler(config=AirTrustConfig(consent_mode=ConsentMode.BLOCK_HIGH_AND_CRITICAL))
