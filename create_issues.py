#!/usr/bin/env python3
import re
import os
import sys
import json
import subprocess

def run_cmd(args, stdin_data=None):
    result = subprocess.run(args, input=stdin_data, text=True, capture_output=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Error running command {' '.join(args)}: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout

def parse_tasks(tasks_file):
    if not os.path.exists(tasks_file):
        print(f"Tasks file not found: {tasks_file}", file=sys.stderr)
        return []
        
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    tasks = []
    lines = content.split('\n')
    current_phase = ""
    current_task = None
    mode = None
    
    for line in lines:
        if line.startswith('## Phase '):
            current_phase = line.replace('## ', '').strip()
            continue
            
        task_match = re.match(r'^###\s*(\[TASK-\d+\])\s*(.*)', line)
        if task_match:
            if current_task:
                tasks.append(current_task)
            task_id = task_match.group(1)
            task_title = task_match.group(2).replace(' (완료)', '').strip()
            current_task = {
                'id': task_id,
                'title': f"{task_id} {task_title}",
                'phase': current_phase,
                '목적': '',
                '세부 작업': '',
                '선행 작업': '',
                '완료 조건': '',
                '테스트 필요': '',
                '결과 파일': ''
            }
            mode = None
            continue
            
        if current_task:
            m = re.match(r'^\*\s*\*\*([^*]+)\*\*:\s*(.*)', line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                if key in current_task:
                    current_task[key] = val
                    mode = key
                else:
                    mode = None
            elif line.startswith('    ') or line.startswith('  -') or line.startswith('  *') or line.startswith('- ') or line.startswith('* '):
                if mode == '세부 작업':
                    current_task['세부 작업'] += '\n' + line
                elif mode:
                    current_task[mode] += '\n' + line
            elif line.strip() == '':
                if mode == '세부 작업' and current_task['세부 작업']:
                    current_task['세부 작업'] += '\n'
            else:
                if mode == '세부 작업':
                    current_task['세부 작업'] += '\n' + line.strip()
                elif mode:
                    current_task[mode] += ' ' + line.strip()
                    
    if current_task:
        tasks.append(current_task)
        
    for t in tasks:
        for k in ['목적', '세부 작업', '선행 작업', '완료 조건', '테스트 필요', '결과 파일']:
            t[k] = t[k].strip()
            
    return tasks

def make_body(task):
    body = []
    body.append("### 📋 Phase")
    body.append(task['phase'])
    body.append("")
    body.append("### 🎯 작업 배경")
    body.append(f"- **목적**: {task['목적']}")
    if task['선행 작업']:
        body.append(f"- **선행 작업**: {task['선행 작업']}")
    if task['결과 파일']:
        body.append(f"- **결과 파일**: {task['결과 파일']}")
    body.append("")
    body.append("### ✍️ 작업 내용")
    body.append(task['세부 작업'])
    body.append("")
    body.append("### ✅ 인수 조건")
    body.append(f"- **완료 조건**: {task['완료 조건']}")
    body.append(f"- **테스트 필요**: {task['테스트 필요']}")
    return "\n".join(body)

def get_existing_issues():
    stdout = run_cmd(["gh", "issue", "list", "--state", "all", "--limit", "200", "--json", "number,title"])
    if not stdout:
        return {}
    issues = json.loads(stdout)
    res = {}
    for issue in issues:
        title = issue['title']
        num = issue['number']
        m = re.search(r'\[(TASK-\d+)\]', title)
        if m:
            res[m.group(0)] = num
    return res

def main():
    tasks = parse_tasks("TASKS.md")
    if not tasks:
        print("No tasks found to register.", file=sys.stderr)
        return
        
    existing_issues = get_existing_issues()
    print(f"Found {len(existing_issues)} existing issues in GitHub.")
    
    for task in tasks:
        task_id = task['id']
        title = task['title']
        body = make_body(task)
        
        if task_id in existing_issues:
            num = existing_issues[task_id]
            print(f"Updating existing issue #{num} for {task_id}...")
            run_cmd(["gh", "issue", "edit", str(num), "--title", title, "-F", "-"], stdin_data=body)
        else:
            print(f"Creating new issue for {task_id}...")
            run_cmd(["gh", "issue", "create", "--title", title, "-F", "-"], stdin_data=body)
            
    print("Done registering issues!")

if __name__ == "__main__":
    main()
