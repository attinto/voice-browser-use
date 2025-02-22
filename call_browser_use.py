#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, BrowserConfig, Browser
import asyncio
from dotenv import load_dotenv
from lmnr import Laminar
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

Laminar.initialize(project_api_key="vq0QbFrHbQrjniDJ1dyRH3PSGWN4lFflnJDFlGXZr4InVakvok97YniMjYCJKwF7") # you can also pass project api key here
load_dotenv()

class BrowserTaskManager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.running = True
        self.worker_thread = None
        self.current_task = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        
    def start(self):
        if not self.worker_thread or not self.worker_thread.is_alive():
            self.running = True
            self.worker_thread = threading.Thread(target=self._process_tasks)
            self.worker_thread.daemon = True
            self.worker_thread.start()
        
    def stop(self):
        self.running = False
        if self.executor:
            self.executor.shutdown(wait=False)
        if self.worker_thread and self.worker_thread.is_alive():
            try:
                self.worker_thread.join(timeout=1.0)  # Wait max 1 second
            except:
                pass  # If thread doesn't join, continue with cleanup
        self.task_queue = queue.Queue()  # Clear pending tasks
        self.result_queue = queue.Queue()  # Clear pending results
        
    def _process_tasks(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=0.5)  # Reduced timeout
                if task:
                    try:
                        self.current_task = task
                        future = self.executor.submit(asyncio.run, self._execute_browser_task(task))
                        result = future.result(timeout=30)  # 30 second timeout for browser tasks
                        self.result_queue.put((task, result))
                    except Exception as e:
                        self.result_queue.put((task, f"Error executing task: {str(e)}"))
                    finally:
                        self.current_task = None
            except queue.Empty:
                continue
            except Exception:
                continue  # Handle any other exceptions gracefully
                
    async def _execute_browser_task(self, task: str):
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

# Singleton instance of the task manager
_task_manager = None

def get_task_manager():
    global _task_manager
    if _task_manager is None:
        _task_manager = BrowserTaskManager()
        _task_manager.start()
    return _task_manager

def run_browser_task(task: str) -> str:
    """
    Función que ejecuta una tarea en el navegador de forma asíncrona y retorna el resultado.
    
    Args:
        task (str): La tarea a realizar
        
    Returns:
        str: El resultado de la tarea o un mensaje de error
    """
    task_manager = get_task_manager()
    task_manager.task_queue.put(task)
    
    # Esperar el resultado
    while True:
        try:
            completed_task, result = task_manager.result_queue.get(timeout=1)
            if completed_task == task:
                return result
            else:
                # Si no es nuestra tarea, volver a ponerla en la cola
                task_manager.result_queue.put((completed_task, result))
        except queue.Empty:
            continue

def cleanup():
    """
    Limpia los recursos del task manager
    """
    global _task_manager
    if _task_manager:
        _task_manager.stop()
        _task_manager = None