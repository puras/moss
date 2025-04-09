import json
import logging

import requests
from ascii_colors import trace_exception
from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse

from app.core.config import settings
from app.core.llm import CompletionsRequest, ChatMessage
from app.modules.edu.biz.prompt import edu_prompt_list

router = APIRouter()

# 学科知识应用
@router.post("/subject_knowledge", summary="学科知识应用", description="学科知识应用")
async def subject_knowledge(request: CompletionsRequest):
    _process_prompt(request, 'subject_knowledge')
    return _chat_completions(request)

# 跨学科关联引用
# interdisciplinary（跨学科的）
@router.post("/inter_disc_cc", summary="跨学科关联引用", description="跨学科关联引用")
async def inter_disc_cc(request: CompletionsRequest):
    _process_prompt(request, 'inter_disc_cc')
    return _chat_completions(request)

# 教育政策解读
# Interpretation of Education Policies
@router.post("/policy_interp", summary="教育政策解读", description="教育政策解读")
async def policy_interp(request: CompletionsRequest):
    _process_prompt(request, 'policy_interp')
    return _chat_completions(request)

# 教材内容总结
@router.post("/summary/textbooks", summary="教材内容总结", description="教材内容总结")
async def summary_textbooks(request: CompletionsRequest):
    _process_prompt(request, 'summary_textbooks')
    return _chat_completions(request)

# 教案内容总结
@router.post("/summary/teaching_plans", summary="教案内容总结", description="教案内容总结")
async def summary_teaching_plans(request: CompletionsRequest):
    _process_prompt(request, 'summary_teaching_plans')
    return _chat_completions(request)

# 考前指导总结
@router.post("/summary/exam_guides", summary="考前指导总结", description="考前指导总结")
async def summary_exam_guides(request: CompletionsRequest):
    _process_prompt(request, 'summary_exam_guides')
    return _chat_completions(request)

# 学习方法问答
@router.post("/chat/learning_methods", summary="学习方法问答", description="学习方法问答")
async def chat_learning_methods(request: CompletionsRequest):
    _process_prompt(request, 'chat_learning_methods')
    return _chat_completions(request)

# 知识概念问答
@router.post("/chat/knowledge_concepts", summary="知识概念问答", description="知识概念问答")
async def chat_knowledge_concepts(request: CompletionsRequest):
    _process_prompt(request, 'chat_knowledge_concepts')
    return _chat_completions(request)

# 教案内容生成
@router.post("/gen/teaching_plans", summary="教案内容生成", description="教案内容生成")
async def gen_teaching_plans(request: CompletionsRequest):
    _process_prompt(request, 'gen_teaching_plans')
    return _chat_completions(request)

# 考题内容生成
@router.post("/gen/exam_questions", summary="考题内容生成", description="考题内容生成")
async def gen_exam_questions(request: CompletionsRequest):
    _process_prompt(request, 'gen_exam_questions')
    return _chat_completions(request)

# 解析知识点，生成思维导图
@router.post("/analyze/knowledge", summary="解析知识点", description="解析知识点")
async def analyze_knowledge(request: CompletionsRequest):
    _process_prompt(request, 'analyze_knowledge')
    return _chat_completions(request)

# 解析自学材料，标注重点、难点、考点
@router.post("/analyze/materials", summary="解析自学材料，标注重点、难点、考点", description="解析自学材料，标注重点、难点、考点")
async def analyze_materials(request: CompletionsRequest):
    _process_prompt(request, 'analyze_materials')
    return _chat_completions(request)

# 课程活动整体结果分析
@router.post("/analyze/activity_results", summary="课程活动整体结果分析", description="课程活动整体结果分析")
async def analyze_activity_results(request: CompletionsRequest):
    _process_prompt(request, 'analyze_activity_results')
    return _chat_completions(request)

# 预设问题回答分析
@router.post("/analyze/answers", summary="预设问题回答分析", description="预设问题回答分析")
async def analyze_answers(request: CompletionsRequest):
    _process_prompt(request, 'analyze_answers')
    return _chat_completions(request)

# 小组活动生成活动引导
@router.post("/gen/activity_guidance", summary="小组活动生成活动引导", description="小组活动生成活动引导")
async def gen_activity_guidance(request: CompletionsRequest):
    _process_prompt(request, 'gen_activity_guidance')
    return _chat_completions(request)

# 多人协作文档与音频生成总结
# multi - person collaboration”
@router.post("/summary/mpc", summary="多人协作文档与音频生成总结", description="多人协作文档与音频生成总结")
async def summary_mpc(request: CompletionsRequest):
    _process_prompt(request, 'summary_mpc')
    return _chat_completions(request)

# 多人协作文档生成演讲稿
@router.post("/gen/mpc_speeches", summary="多人协作文档生成演讲稿", description="多人协作文档生成演讲稿")
async def gen_mpc_speeches(request: CompletionsRequest):
    _process_prompt(request, 'gen_mpc_speeches')
    return _chat_completions(request)


# 问题预演生成
@router.post("/gen/rehearsal_questions", summary="问题预演生成", description="问题预演生成")
async def gen_rehearsal_questions(request: CompletionsRequest):
    _process_prompt(request, 'gen_rehearsal_questions')
    return _chat_completions(request)


# 教学视频总结
@router.post("/summary/teaching_videos", summary="教学视频总结", description="教学视频总结")
async def summary_teaching_videos(request: CompletionsRequest):
    _process_prompt(request, 'summary_teaching_videos')
    return _chat_completions(request)

# 课程讲授建议
# course instruction suggestion
@router.post("/gen/cis", summary="课程讲授建议", description="课程讲授建议")
async def gen_cis(request: CompletionsRequest):
    _process_prompt(request, 'gen_cis')
    return _chat_completions(request)



def _process_prompt(request: CompletionsRequest, target: str):
    messages = request.messages
    prompt_msg = ChatMessage(role="system", content=edu_prompt_list[target]["content"])
    messages.append(prompt_msg)
    logging.info(f"request: {request}")


def _chat_completions(request: CompletionsRequest):
    try:
        messages = request.messages
        if not messages:
            raise HTTPException(status_code=400, detail="消息列表不能为空")

        # 转换消息格式为Ollama格式
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # 准备请求数据
        data = {
            "model": request.model or settings.LLM_MODEL_NAME or "deepseek-r1:32b",
            "messages": ollama_messages,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature or 0.5
            }
        }

        if request.stream:
            async def stream_generator():
                # 使用requests进行流式请求
                response = requests.post(
                    f"{settings.LLM_MODEL_HOST}/api/chat",
                    json=data,
                    stream=True
                ) if settings.LLM_MODEL == 'ollama' else requests.post(
                    f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                    json=data,
                    stream=True
                )

                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "error" in chunk:
                                yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                                continue

                            chunk_data = {
                                "choices": [{
                                    "delta": {"content": chunk.get("message", {}).get("content", "")},
                                    "finish_reason": "stop" if chunk.get("done", False) else None,
                                    "index": 0
                                }]
                            }
                            yield f"data: {json.dumps(chunk_data)}\n\n"

                            # if chunk.get("done", False):
                            #     yield "data: [DONE]\n\n"
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON decode error: {str(e)}")
                            continue

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # 非流式请求
            response = requests.post(
                f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                json=data
            ) if settings.LLM_MODEL == 'ollama' else requests.post(
                f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                json=data,
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result.get("message", {}).get("content", "")
                    },
                    "finish_reason": "stop",
                    "index": 0
                }]
            }

    except Exception as e:
        trace_exception(e)
        raise HTTPException(status_code=500, detail=str(e))