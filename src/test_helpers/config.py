from unittest.mock import Mock


def mock_config(**kwargs):
    mocked_config = Mock()
    for k, v in kwargs.items():
        setattr(mocked_config, k.upper(), v)
    return mocked_config
