import json

response = """
```json
{
    "questions": [
        {
            "question": "CIPP模型的过程评价包括哪些具体步骤？"
        },
        {
            "question": "在CIPP模型的成果评价中，如何衡量干预措施的有效性？"
        },
        {
            "question": "基于设计的研究（DBR）的主要特征是什么？"
        },
        {
            "question": "DBR通用模型的核心阶段包括哪些内容？"
        },
        {
            "question": "DBR三个阶段的要素和产出分别是什么？"
        },
        {
            "question": "基于设计的研究与预测性研究有何区别？"
        },
        {
            "question": "在DBR中，分析和探索阶段的主要任务有哪些？"
        },
        {
            "question": "设计和建构阶段需要拟定哪些初步原则来指导干预的设计？"
        },
        {
            "question": "评价和反思阶段的产出包括哪些内容？"
        },
        {
            "question": "DBR产生的解决方案主要有哪些类型？"
        },
        {
            "question": "如何理解基于设计的研究中的'迭代性'特征？"
        },
        {
            "question": "在DBR中，理论与实践是如何结合的？"
        }
    ]
}
```
"""

questions = extract_json_from_llm_output(response)

with open(file) as f:
    content = json.loads(f.read())
    for chunk in content:
        questions = chunk['questions']
        for question in questions:
            if isinstance(question, dict):
                print(chunk["chunkId"] + "-----" + question["question"])