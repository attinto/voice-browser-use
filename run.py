#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, BrowserConfig, Browser
import asyncio
from dotenv import load_dotenv
from lmnr import Laminar

# Laminar.initialize() # you can also pass project api key here
load_dotenv()

async def main():

    # Basic configuration
    config = BrowserConfig(
        headless=False,
        disable_security=True,
        chrome_instance_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )

    browser = Browser(config=config)

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    agent = Agent(
        task="¿Qué temperatura hace en Madrid?",
        llm = llm,
        use_vision=False,
        planner_llm=llm,
        browser=browser
    )
    result = await agent.run()
    output=result.final_result()
    print(output)

asyncio.run(main())