from utils.pre_start_init import app


@app.get("/")
async def root():
    print("Зашли в root")

    return {"error": True,
            "data": "No_service_selected",
            # "available_services": ["Vosk_Recognizer"],
            "comment": "try_addr: https://law-services.amulex.ru/Classifier/docs"}