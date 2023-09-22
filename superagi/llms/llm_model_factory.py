from sqlalchemy.orm import sessionmaker

from superagi.llms.google_palm import GooglePalm
from superagi.llms.hugging_face import HuggingFace
from superagi.llms.ooba_booga import OobaBooga
from superagi.llms.openai import OpenAi
from superagi.llms.replicate import Replicate
from superagi.local_llms import OOBA_PROVIDER
from superagi.models.db import connect_db
from superagi.models.models import Models
from superagi.models.models_config import ModelsConfig


def get_model(organisation_id, api_key, model="gpt-3.5-turbo", **kwargs):
    print("Fetching model details from database...")
    engine = connect_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    model_instance = (
        session.query(Models)
        .filter(Models.org_id == organisation_id, Models.model_name == model)
        .first()
    )
    response = (
        session.query(ModelsConfig.provider)
        .filter(
            ModelsConfig.org_id == organisation_id,
            ModelsConfig.id == model_instance.model_provider_id,
        )
        .first()
    )
    provider_name = response.provider

    session.close()

    if provider_name == "OpenAI":
        print("Provider is OpenAI")
        return OpenAi(model=model_instance.model_name, api_key=api_key, **kwargs)
    elif provider_name == "Replicate":
        print("Provider is Replicate")
        return Replicate(
            model=model_instance.model_name,
            version=model_instance.version,
            api_key=api_key,
            **kwargs
        )
    elif provider_name == "Google Palm":
        print("Provider is Google Palm")
        return GooglePalm(model=model_instance.model_name, api_key=api_key, **kwargs)
    elif provider_name == "Hugging Face":
        print("Provider is Hugging Face")
        return HuggingFace(
            model=model_instance.model_name,
            end_point=model_instance.end_point,
            api_key=api_key,
            **kwargs
        )
    elif provider_name == OOBA_PROVIDER:
        print("Provider is Ooba Booga")
        return OobaBooga(**kwargs)
    else:
        print("Unknown provider.")


def build_model_with_api_key(provider_name, api_key):
    if provider_name.lower() == "openai":
        return OpenAi(api_key=api_key)
    elif provider_name.lower() == "replicate":
        return Replicate(api_key=api_key)
    elif provider_name.lower() == "google palm":
        return GooglePalm(api_key=api_key)
    elif provider_name.lower() == "hugging face":
        return HuggingFace(api_key=api_key)
    elif provider_name.lower() == OOBA_PROVIDER.lower():
        return OobaBooga()
    else:
        print("Unknown provider.")
