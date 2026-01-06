import argparse

MODELS = ['gemini-3-flash', 'gemini-2.5-flash', 'deepseek-V3.1', 'deepseek-R1']

def parse_arguments_generator():
    parser = argparse.ArgumentParser(description = 'Patch correction generation comparison between different LLM models.')

    parser.add_argument('report_filepath', help='Filepath containing OpenVAS report.') 
    parser.add_argument('LLM_model', choices=MODELS, help='LLM model for correction patch generation.') 
    
    return parser.parse_args()


def parse_arguments_validator():
    parser = argparse.ArgumentParser(description = 'Validator tasked to choose the best correction patch amongst available.')

    parser.add_argument('Patches_directory_filepath', help='Directory filepath containing correction patches.') 

    return parser.parse_args()
