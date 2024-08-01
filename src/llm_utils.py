from typing import List, Callable
from googletrans import Translator
import random

from src.prompt_configs import PromptConfig, prefix

translator = Translator()

def get_translation(text: str, dest: str = 'en') -> str:
    return translator.translate(text, dest=dest).text

def llm_generate_titles(
    llm_generate: Callable[[str], str], 
    description: str, 
    prompt_config: PromptConfig,
) -> List[str]:
    """
    Generate presentation slide titles using a language model.

    Args:
        llm_generate (Callable[[str], str]): Function to generate text using a language model.
        description (str): Description of the presentation.
        prompt_config (PromptConfig): Configuration for prompts.

    Returns:
        List[str]: List of generated slide titles.
    """
    prompt = prompt_config.title_prompt.format(
        description=description
    )
    titles_str = llm_generate(prompt)
    titles = []
    for title in titles_str.split("\n"):
        sep_index = title.index('. ') + 2
        title = title.strip()[sep_index:]
        title = title.replace('.', '')
        title = title.replace('\n', '')
        if prefix in title.lower():
            title = title[
                title.lower().index(prefix)+len(prefix):
            ]
        titles.append(title)
    return titles

def llm_generate_text(
    llm_generate: Callable[[str], str], 
    description: str, 
    titles: List[str], 
    prompt_config: PromptConfig
) -> List[str]:
    """
    Generate text for each slide title using a language model.

    Args:
        llm_generate (Callable[[str], str]): Function to generate text using a language model.
        description (str): Description of the presentation.
        titles (List[str]): List of slide titles.
        prompt_config (PromptConfig): Configuration for prompts.

    Returns:
        List[str]: List of generated texts for each slide.
    """
    texts = []
    for title in titles:
        query = prompt_config.text_prompt.format(description=description, title=title)
        text = llm_generate(query)
        if prefix in text.lower():
            text = text[text.lower().index(prefix)+len(prefix):]
            text = text.replace('\n', '') 
        texts.append(text)
    return texts

def llm_generate_image_prompt(
    llm_generate: Callable[[str], str], 
    description: str, 
    title: str, 
    prompt_config: PromptConfig
) -> str:
    """
    Generate an image prompt for a slide using a language model and translate it.

    Args:
        llm_generate (Callable[[str], str]): Function to generate text using a language model.
        description (str): Description of the presentation.
        title (str): Slide title.
        prompt_config (PromptConfig): Configuration for prompts.

    Returns:
        str: Translated image prompt.
    """
    query = prompt_config.image_prompt.format(description=description, title=title)
    prompt = llm_generate(query)
    if prefix in prompt: 
        prompt = prompt[prompt.lower().index(prompt)+len(prompt):]
        prompt = prompt.replace('\n', '')
    return get_translation(prompt)

def llm_generate_background_prompt(
    llm_generate: Callable[[str], str], 
    description: str, 
    title: str, 
    prompt_config: PromptConfig, 
    background_style: str = ''
) -> str:
    """
    Generate a background prompt for a slide using a language model and translate it.

    Args:
        llm_generate (Callable[[str], str]): Function to generate text using a language model.
        description (str): Description of the presentation.
        title (str): Slide title.
        prompt_config (PromptConfig): Configuration for prompts.

    Returns:
        str: Translated background prompt.
    """
    query = prompt_config.background_prompt.format(description=description, title=title)
    
    keywords = llm_generate(query)
    background_prompt = f'{keywords}, {background_style}'
        
    return get_translation(background_prompt)