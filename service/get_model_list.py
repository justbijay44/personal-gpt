from config.settings import Settings

settings = Settings()

def get_ollama_models_list():
    models_list = settings.OLLAMA_MODELS
    ollama_model = [model.strip() for model in models_list.split(",") if model.strip()]
    return models_list

# testing
# check_ollama_models = get_ollama_models_list()
# print(type(check_ollama_models))
# print(check_ollama_models)