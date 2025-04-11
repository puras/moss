import json

file = '../local-db/000000/questions.json'

with open(file) as f:
    content = json.loads(f.read())
    for chunk in content:
        questions = chunk['questions']
        for question in questions:
            if isinstance(question, dict):
                print(chunk["chunkId"] + "-----" + question["question"])