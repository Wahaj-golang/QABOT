import os
import json
import requests
import ollama
from typing import List, Dict
from generate import generate_pdf


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
    """Analyze code using Qwen model through Ollama API"""
    prompt = f"""
    Analyze this code and return JSON with:
    1. code_quality_rating (0-10) in every aspect of coding, also give reason for the rating as well.
    2. tech_stack (list of frameworks/libs), give brief descriptions
    3. total_functions (count), give names
    4. total_loops (count)
    5. total_classes (count)
    
    Code:
    {code}
    
    Return ONLY valid JSON format:
    """
    
    try:
        response = ollama.chat(model="qwen2.5:3b", messages=[{"role":"user", "content": prompt}], format='json')
        # response = requests.post(
        #     'http://localhost:11434/api/generate',
        #     json={
        #         'model': 'qwen',
        #         'prompt': prompt,
        #         'format': 'json',
        #         'stream': False
        #     }
        # )
        result = response["message"]["content"]
        # return json.loads(response.model_dump_json()['response'])
        return json.loads(result)
    except Exception as e:
        print(f"Analysis error: {e}")
        return {}

def process_project(project_path: str):
    """Process all code files in project"""
    code_files = get_code_files(project_path)
    project_report = {
        'code_quality': [],
        'tech_stack': set(),
        'total_functions': 0,
        'total_loops': 0,
        'total_classes': 0
    }

    for file_path in code_files:
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                analysis = analyze_code_with_ollama(code)
                
                if analysis:
                    project_report['code_quality'].append(analysis.get('code_quality_rating', 0))
                    project_report['tech_stack'].update(analysis.get('tech_stack', []))
                    project_report['total_functions'] += analysis.get('total_functions', 0)
                    project_report['total_loops'] += analysis.get('total_loops', 0)
                    project_report['total_classes'] += analysis.get('total_classes', 0)
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