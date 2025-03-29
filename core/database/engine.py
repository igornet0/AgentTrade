# запуск движка ORM

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.database.models import Base
from core.database.orm_query import (orm_update_coin_list, 
                                     orm_add_timeseries,
                                     orm_get_timeseries,
                                     orm_update_timeseries_path)

from core.utils.handlers import CoinHandler

from core.config import settings, settings_trade

import logging

logger = logging.getLogger("DB.engine")

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():

    logger.info("Create database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database created")

    async with session_maker() as session:
        await orm_update_coin_list(session, CoinHandler.coin_list)
        for coin in CoinHandler.coin_list:
            dataset_path = CoinHandler.get_path_dataset(coin=coin, 
                                                        timestamp=settings_trade.TIMETRAVEL,
                                                        type_dataset=settings_trade.TYPE_DATASET_FOR_COIN, 
                                                        root_path=settings_trade.PROCESSED_DATA_PATH)
            

            timeseries = [ts.path_dataset for ts in await orm_get_timeseries(session, coin, settings_trade.TIMETRAVEL)]

            result = []
            for path in dataset_path:
                if path not in timeseries:
                    result.append(await orm_add_timeseries(session, coin, settings_trade.TIMETRAVEL, path))
                else:
                    await orm_update_timeseries_path(session, coin, settings_trade.TIMETRAVEL, path)
            
            if not result:
                logger.error(f"Dataset for {coin} not added")
                continue

            logger.info(f"Dataset for {coin} added")
    
    logger.info("Database updated")
            
            
            # dataset_path =    map(lambda **kwargs: orm_update_timeseries_path(session, **kwargs), 
            #                       dataset_path) 

    # открываем сессию и записываем категории при старте бота и описание для страниц баннера
    # async with session_maker() as session:
    #     await orm_create_sirops(session, sirops)
    #     await orm_create_categories(session, categories.keys())
    #     await orm_create_podcategories(session, categories)
    #     await org_add_product(session, categories)
    #     await orm_create_dop(session, milk)
    #     await orm_create_places(session, places)
    #     await orm_add_banner_description(session, description_for_info_pages)


# функция для сброса таблиц в БД
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)