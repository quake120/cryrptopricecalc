import aiohttp
import streamlit as st
import json
import datetime
import asyncio

BASEURL = "https://api.coingecko.com/api/v3/"
COININFOURL = "coins/"


async def main():
    with st.form('info_form'):
        crypto_name = st.text_input("Enter a crypto ticker")
        purchase_date = st.date_input("What date did you buy this crypto?")
        shares = st.number_input("How many coins/shares of {crypto_name} did you buy?".format(crypto_name=crypto_name))

        submitted = st.form_submit_button(label="Go!")

        if submitted:
            await calculate_prices(crypto_name, purchase_date, shares)


async def calculate_prices(crypto_name, purchase_date, shares):
    currentPricingInfo = await getCryptoInfo(crypto_name)
    historicalPricingInfo = await getCryptoHistory(crypto_name, purchase_date.strftime("%d-%m-%Y"))
    try:
        historyPrice = historicalPricingInfo['market_data']['current_price']['usd']
    except Exception as e:
        st.error("Something went wrong. Your purchase date might be too far back")
        return

    currentPrice = currentPricingInfo['market_data']['current_price']['usd']
    market_range = await getCryptoHistoryDates(purchase_date, crypto_name)

    currentHigh = market_range['prices'][0][1]
    currentLow = market_range['prices'][0][1]

    for price in market_range['prices']:
        if price[1] > currentHigh:
            currentHigh = price[1]
        if price[1] < currentLow:
            currentLow = price[1]

    print(currentHigh)
    print(currentLow)

    hstFmtPrice = str("\${:,.4f}".format(historyPrice))
    hstFmtTotal = str("\${:,.4f}".format(historyPrice * shares))
    curFmtPrice = str("\${:,.4f}".format(currentPrice))
    curFmtTotal = str("\${:,.4f}".format(currentPrice * shares))
    curHighFmt = str("\${:,.4f}").format(currentHigh)
    curLowFmt = str("\${:,.4f}").format(currentLow)

    profit = (currentPrice * shares) - (historyPrice * shares)

    profitFmt = str("\${:,.4f}".format(profit))
    profitOrLoss = "loss"

    if profit > 0:
        profitOrLoss = "Profit"
    else:
        profitOrLoss = "Loss"

    # st.write(f"On {purchase_date}, the value of {crypto_name} was {hstFmtPrice}. "
    #        f"Your {shares} shares were worth {hstFmtTotal} at that time. "
    #       f"{crypto_name}'s value today is {curFmtPrice}. "
    #       f"Your {shares} shares are worth {curFmtTotal} today, a {profitOrLoss} of {profitFmt}. "
    #       f"The lowest price between {purchase_date} and {datetime.datetime.now()} was {curLowFmt}. The high price "
    #       f"between those dates is {curHighFmt}",
    #       unsafe_allow_html=False)

    st.info(f"Price of {crypto_name} at purchase: {hstFmtPrice}")
    st.info(f"Value of {shares} shares at purchase: {hstFmtTotal}")
    st.info(f"Price of {crypto_name} today: {curFmtPrice}")
    st.info(f"Value of {shares} shares today {curFmtTotal}")
    st.info(f"{profitOrLoss} of {profitFmt}")
    st.info(f"Highest price between {purchase_date} and {datetime.datetime.now()}: {curHighFmt}")
    st.info(f"Lowest price between {purchase_date} and {datetime.datetime.now()}: {curLowFmt}")


async def api(url, params):
    async with aiohttp.ClientSession() as session:
        res = await session.get(url, params=params)
        return await res.json()


async def getCryptoInfo(coin_ticker):
    async with aiohttp.ClientSession() as session:
        res = await session.get(BASEURL + f"coins/{coin_ticker}")
        return await res.json()


async def getCryptoHistory(coin_ticker, date):
    headers = {"id": coin_ticker,
               "date": date}
    async with aiohttp.ClientSession() as session:
        res = await session.get(BASEURL + f"/coins/{coin_ticker}/history"
                                , params=headers)
        return await res.json()


async def getCryptoHistoryDates(start_date, coin_ticker):
    startTimestamp = datetime.datetime.timestamp(datetime.datetime(start_date.year, start_date.month, start_date.day,
                                                                   start_date.timetuple().tm_hour,
                                                                   start_date.timetuple().tm_min))

    endTimestamp = datetime.datetime.timestamp(datetime.datetime.now())

    params = {
        "from": startTimestamp,
        "to": endTimestamp,
        "vs_currency": "usd"
    }

    res = await api(BASEURL + f"/coins/{coin_ticker}/market_chart/range", params=params)
    return res


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
