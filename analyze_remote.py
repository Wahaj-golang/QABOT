import os
import json
import requests
import ollama
from ollamaserver import OllamaClient
from typing import List, Dict
from generate import generate_pdf

client = OllamaClient()

def get_code_files(root_dir: str):
    """Get all code files from project directory"""
    code_extensions = ['.py', '.js', '.java', '.cpp', '.c', '.ts', '.go']
    ignore_dirs = ['venv', 'node_modules', '.git', '__pycache__']
    
    code_files = []
    for root, dirs, files in os.walk(root_dir):
        [dirs.remove(d) for d in list(dirs) if d in ignore_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in code_extensions):
                code_files.append(os.path.join(root, file))
    return code_files

def analyze_code_with_ollama(code: str):
    """Analyze code"""
    prompt = f"""
    Analyze this code and return JSON with:
    1. code_quality_rating (0-10) in every aspect of coding, also give reasons for the ratings as well.
    2. tech_stack (list of frameworks/libs), give brief descriptions
    3. total_functions (count), give names of the functions
    4. total_loops (count), give only counts of the loops or recursions
    5. total_classes (count), give names of the classes
    
    Code:
    {code}
    
    Return ONLY valid JSON format:
    """
    
    try:
        # response = ollama.chat(model="qwen2.5:3b", messages=[{"role":"user", "content": prompt}], format='json')
        response = client.generate_response(messages=[{"role":"system", "content": "Always Response with Valid Json format"},{"role":"user", "content": prompt}], model_name="deepseek-r1")

        result = response["message"]["content"]
        # return json.loads(response.model_dump_json()['response'])
        return clean(result)
    except Exception as e:
        print(f"Analysis error: {e}")
        return {}
    
def clean(json_string):
    json_prompt = f"""Extract Valid Json From this string, if its not a valid json then fix it and reply with only json, heres the string: {json_string}"""
    response = client.generate_response(messages=[{"role":"user", "content": json_prompt}], model_name="llama3.2")
    fixed_string = response["message"]["content"]
    return clean_json_string(fixed_string)

def clean_json_string(json_string):
    lines = json_string.splitlines()
    valid_lines = []
    inside_json = False
    open_braces = 0

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if line.startswith("{"):  # Start of JSON object
            inside_json = True
            open_braces += 1  # Count opening braces
        if inside_json:
            valid_lines.append(line)  # Add line to valid lines
        if line.endswith("}"):  # End of JSON object
            open_braces -= 1
            if open_braces == 0:
                break  # Found the outermost closing brace, exit loop
    
    for i in range(len(valid_lines)-1, 0, -1):
        if valid_lines[i] == "}":
            cleaned_json_string = "".join(valid_lines[:i+1])
            break
    
    return json.loads(cleaned_json_string)


def process_project(project_path: str):
    """Process all code files in project"""
    code_files = get_code_files(project_path)
    project_report = {
        'code_quality': [],
        'tech_stack': [],
        'total_functions': [],
        'total_loops': [],
        'total_classes': []
    }

    for file_path in code_files:
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                analysis = analyze_code_with_ollama(code)
                
                if analysis:
                    project_report['code_quality'].append(analysis.get('code_quality_rating', 0))
                    project_report['tech_stack'].append(analysis.get('tech_stack', []))
                    # project_report['total_functions'] += analysis.get('total_functions', 0)
                    # project_report['total_loops'] += analysis.get('total_loops', 0)
                    # project_report['total_classes'] += analysis.get('total_classes', 0)

                    project_report['total_functions'].append(analysis.get('total_functions', 0))
                    project_report['total_loops'].append(analysis.get('total_loops', 0))
                    project_report['total_classes'].append(analysis.get('total_classes', 0))
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # project_report['tech_stack'] = list(project_report['tech_stack'])
    # project_report['code_quality'] = sum(project_report['code_quality'])/len(project_report['code_quality']) if project_report['code_quality'] else 0
    
    return project_report

if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("project_path", help="Path to project directory")
    # parser.add_argument("--output", default="quality_report.pdf", help="Output PDF path")
    # args = parser.parse_args()
    # report = process_project(args.project_path)
    # generate_pdf(report, args.output)
    # print(f"Report generated at {args.output}")
    report = process_project("D:\projects\Haggle_Chatbot")
    generate_pdf(report)
    print("REPORT GENERATED!")