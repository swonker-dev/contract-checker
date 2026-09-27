from contract_checker.config import Settings


def test_empty_ca_bundle_is_none() -> None:
    settings = Settings(_env_file=None, gigachat_ca_bundle_file="")

    assert settings.gigachat_ca_bundle_file is None

