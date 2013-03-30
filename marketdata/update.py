# -*- coding:utf-8 -*-
'''
Market data update functionality
'''
from __future__ import print_function
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import schema
from schema import Symbol, HistoricalPrice
import yahoo


def update_marketdata():
    session = sessionmaker(bind=schema.engine)()
    query_result = session.query(Symbol, func.max(HistoricalPrice.date)).outerjoin(HistoricalPrice, Symbol.name == HistoricalPrice.symbol).group_by(Symbol)
    #from_date = datetime.now() - timedelta(days=10*365)  # fetch market data for 10 years
    from_date = datetime.now() - timedelta(days=10)  # temp
    to_date = datetime.now() + timedelta(days=2)  # use a future date since there might be issues with timezones
    for (symbol, date) in query_result:
        fdate = date + timedelta(days=1) if date is not None else from_date
        (res, data) = yahoo.fetch_market_data(symbol.name, fdate, to_date)
        if res:
            session.add_all([HistoricalPrice(x[0], symbol.name, x[1], x[2], x[3], x[4], x[5], x[6]) for x in data])
            session.commit()
        else:
            print('Failed updating symbol %s' % symbol.name)


def test():
    session = sessionmaker(bind=schema.engine)()
    return session.query(Symbol, func.max(HistoricalPrice.date)).outerjoin(HistoricalPrice, Symbol.name == HistoricalPrice.symbol).group_by(Symbol)
