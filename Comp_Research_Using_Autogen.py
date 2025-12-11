from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_community.utilities import SerpAPIWrapper
import asyncio
import env
# os.environ["GOOGLE_API_KEY"] = "..."
# os.environ["GOOGLE_SEARCH_ENGINE_ID"] = "..."

def get_glassdoor_rating(query: str):
    search = SerpAPIWrapper()
    result = search.run(f"{query} Glassdoor rating")
    return (result)


glassdoor_rating_tool = FunctionTool(
    get_glassdoor_rating, description="Search Google for information, returns results with a snippet and body content"
)

def get_director_info(query: str):
    search = SerpAPIWrapper()
    result = search.run(f"{query} director information site:zaubacorp.com")
    return (result)

director_info_tool = FunctionTool(
    get_director_info, description="Search Zaubacorp for director information and returns results with a snippet and body content"
)

def analyze_stock(ticker: str) -> dict:  # type: ignore[type-arg]
    import os
    from datetime import datetime, timedelta

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import yfinance as yf
    from pytz import timezone  # type: ignore

    stock = yf.Ticker(ticker)

    # Get historical data (1 year of data to ensure we have enough for 200-day MA)
    end_date = datetime.now(timezone("UTC"))
    start_date = end_date - timedelta(days=365)
    hist = stock.history(start=start_date, end=end_date)

    # Ensure we have data
    if hist.empty:
        return {"error": "No historical data available for the specified ticker."}

    # Compute basic statistics and additional metrics
    current_price = stock.info.get("currentPrice", hist["Close"].iloc[-1])
    year_high = stock.info.get("fiftyTwoWeekHigh", hist["High"].max())
    year_low = stock.info.get("fiftyTwoWeekLow", hist["Low"].min())

    # Calculate 50-day and 200-day moving averages
    ma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]
    ma_200 = hist["Close"].rolling(window=200).mean().iloc[-1]

    # Calculate YTD price change and percent change
    ytd_start = datetime(end_date.year, 1, 1, tzinfo=timezone("UTC"))
    ytd_data = hist.loc[ytd_start:]  # type: ignore[misc]
    if not ytd_data.empty:
        price_change = ytd_data["Close"].iloc[-1] - ytd_data["Close"].iloc[0]
        percent_change = (price_change / ytd_data["Close"].iloc[0]) * 100
    else:
        price_change = percent_change = np.nan

    # Determine trend
    if pd.notna(ma_50) and pd.notna(ma_200):
        if ma_50 > ma_200:
            trend = "Upward"
        elif ma_50 < ma_200:
            trend = "Downward"
        else:
            trend = "Neutral"
    else:
        trend = "Insufficient data for trend analysis"

    # Calculate volatility (standard deviation of daily returns)
    daily_returns = hist["Close"].pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252)  # Annualized volatility

    # Create result dictionary
    result = {
        "ticker": ticker,
        "current_price": current_price,
        "52_week_high": year_high,
        "52_week_low": year_low,
        "50_day_ma": ma_50,
        "200_day_ma": ma_200,
        "ytd_price_change": price_change,
        "ytd_percent_change": percent_change,
        "trend": trend,
        "volatility": volatility,
    }

    # Convert numpy types to Python native types for better JSON serialization
    for key, value in result.items():
        if isinstance(value, np.generic):
            result[key] = value.item()

    # Generate plot
    plt.figure(figsize=(12, 6))
    plt.plot(hist.index, hist["Close"], label="Close Price")
    plt.plot(hist.index, hist["Close"].rolling(window=50).mean(), label="50-day MA")
    plt.plot(hist.index, hist["Close"].rolling(window=200).mean(), label="200-day MA")
    plt.title(f"{ticker} Stock Price (Past Year)")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.grid(True)

    # Save plot to file
    os.makedirs("coding", exist_ok=True)
    plot_file_path = f"coding/{ticker}_stockprice.png"
    plt.savefig(plot_file_path)
    print(f"Plot saved as {plot_file_path}")
    result["plot_file_path"] = plot_file_path

    return result

stock_analysis_tool = FunctionTool(analyze_stock, description="Analyze stock data and generate a plot")

planning_agent = AssistantAgent( 
    name="Planning_Agent",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="""You are a planning agent. 
    Your job is to break the tasks into smaller, manageable subtasks.
    Your team members are :
    Company_researcher : Summarizes about the company
    Finance_analyst : Reports the current finance status of the company
    Review_analyst : Reports the glassdoor review of the company.  Only the review ratings.
    Director_Info : Retrieves the Director's information of the company from Zaubacorp website

    You have to plan and delegate the tasks - you do not execute them yourself.

    When assigning tasks use the following format:
    1. <Agent> : <task>

    After all tasks are done, summarize the findings and end with "TERMINATE" to end the conversation.

    """

)

company_researcher = AssistantAgent( 
    name="Company_Researcher",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You are a helpful AI assistant which will summarize about the company in less than 100 words"
)

finance_analyst = AssistantAgent(
    name="Finance_Analyst",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    tools=[stock_analysis_tool], ## unfortunately this tool will fetch the stock details from ticker which works only for US companies
    system_message="You are a helpful AI assistant which provides the finance status of the company. Provide Revenue, Profit and quick Financial report",
)

director_info = AssistantAgent(
    name="Director_Info_Agent",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
     tools=[director_info_tool],  ## unfortunately this tool will fetch the director details from Zaubacorp which works only for Indian companies
    system_message="You are a helpful AI assistant which retrieves the Director's information of the company from Zaubacorp website"
)

review_analyst = AssistantAgent(
    name="Review_Analyst",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    tools=[glassdoor_rating_tool],
    system_message="You are a helpful AI assistant which retrieves the glassdoor ratings of the company",
)

termination = TextMentionTermination("TERMINIATE") | MaxMessageTermination(max_messages=10)

team = SelectorGroupChat([planning_agent, company_researcher, finance_analyst, director_info, review_analyst], 
                        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
                        termination_condition=termination)

async def main():
    while True:
        query = input("Enter company name to research (type 'exit' to quit) : ")
        if query.lower() == "exit":
            break
        print(query)
        task = "Write about the company " + query
        stream = team.run_stream(task=task)
        await Console(stream)

if __name__ == "__main__":
  asyncio.run(main())

