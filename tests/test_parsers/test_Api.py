import pytest

from apps.data_parser import ParserApi


class TestParserApi:
    
    def test_init(self):
        parser = ParserApi()
        assert parser

        # with pytest.raises(NotImplementedError):
        #     parser.start_web("https://example.com")

        # with pytest.raises(NotImplementedError):
        #     parser.start_parser()