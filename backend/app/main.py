from .core.app import App

app_instance = App()

app = app_instance.fastapi_app

if __name__ == "__main__":
    app_instance.start()