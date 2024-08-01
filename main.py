import time
import argparse
from src.constructor import generate_presentation 
from src.prompt_configs import en_gigachat_config, ru_gigachat_config
from src.gigachat import giga_generate
from src.kandinsky import api_k31_generate
from src.font import Font

def main():
    parser = argparse.ArgumentParser(
        description='Generate a presentation.'
    )
    parser.add_argument(
        '-d', '--description', 
        type=str, 
        required=True, 
        help='Description of the presentation'
    )
    parser.add_argument(
        '-l', '--language', 
        type=str, 
        choices=['en', 'ru'], 
        default='en', 
        help='Language for the presentation. Choices are: English, Russian. Default is English.'
    )
    args = parser.parse_args()

    # Select the appropriate prompt configuration based on the language argument
    if args.language == 'en':
        prompt_config = en_gigachat_config
    elif args.language == 'ru':
        prompt_config = ru_gigachat_config
    else: 
        # set default to prevent interruptions in unexpected scenario
        print("only 'en' and 'ru' configs are available, settings default 'en'")
        prompt_config = en_gigachat_config

    fonts_dir = "./fonts"
    logs_dir = "./logs"
    
    font = Font(fonts_dir)
    font.set_random_font() 
    
    output_dir = f'{logs_dir}/{int(time.time())}'
    
    generate_presentation(
        llm_generate=giga_generate, 
        generate_image=api_k31_generate,
        prompt_config=prompt_config,    
        description=args.description,
        font=font,
        output_dir=output_dir,
    )

if __name__ == "__main__": 
    main()