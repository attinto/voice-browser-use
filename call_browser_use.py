#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, BrowserConfig, Browser
import asyncio
from dotenv import load_dotenv
from lmnr import Laminar

Laminar.initialize(project_api_key="vq0QbFrHbQrjniDJ1dyRH3PSGWN4lFflnJDFlGXZr4InVakvok97YniMjYCJKwF7") # you can also pass project api key here
load_dotenv()

async def get_browser_response(task: str) -> str:
    """
    Función que ejecuta una tarea en el navegador y retorna el resultado.
    
    Args:
        task (str): La tarea a realizar, por ejemplo "¿Qué temperatura hace en Madrid?"
        
    Returns:
        str: El resultado de la tarea
    """
    # Basic configuration
    config = BrowserConfig(
        headless=False,
        disable_security=True,
        chrome_instance_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )

    browser = Browser(config=config)
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    agent = Agent(
        task=task,
        llm=llm,
        use_vision=False,
        planner_llm=llm,
        browser=browser
    )
    result = await agent.run()
    return result.final_result()

def run_browser_task(task: str) -> str:
    """
    Función sincrónica que envuelve la función asíncrona para facilitar su uso.
    
    Args:
        task (str): La tarea a realizar
        
    Returns:
        str: El resultado de la tarea
    """
    return asyncio.run(get_browser_response(task))