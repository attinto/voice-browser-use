from call_browser_use import run_browser_task

def main():
    # Ejemplo de uso de la función
    task = "¿Qué temperatura hace en Madrid?"
    resultado = run_browser_task(task)
    print(f"Resultado de la tarea: {resultado}")

if __name__ == "__main__":
    main() 