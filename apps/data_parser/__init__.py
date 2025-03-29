from apps.data_parser.data import DataParser
from apps.data_parser.Api import ParserApi
from apps.data_parser.parsers import ParserNews, ParserKucoin
from apps.data_parser.handler import Handler as HandlerParser
# from .parser_bcs import Parser_bcs
# from .parser_marketcap import Parser_marketcap
# from .parser_kucoin import Parser_kucoin
# from .parser_news import Parser_news

__all__ = ["DataParser", "ParserApi", "ParserNews", "ParserKucoin", "HandlerParser"]