import argparse
import os
import sys

from ascii_colors import ASCIIColors

from app import __version__ as core_version
from app.core.config import settings


def check_env_file():
    if not os.path.exists(".env"):
        warning_msg = "Warning: Startup directory must contain .env file for multi-instance support."
        ASCIIColors.yellow(warning_msg)

        if sys.stdin.isatty():
            response = input("Do you want to continue? [yes/no]: ")
            if response.lower() != "yes":
                ASCIIColors.red("Server startup cancelled")
                return False
    return True

def parse_args(is_uvicorn_mode: bool=False):
    parser = argparse.ArgumentParser(
        description="MOSS FastAPI Server with separate working and input directories"
    )

    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="Server host (default: from env or 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=os.getenv("PORT", "8000"),
        help="Server port (default: from env or 8000)",
    )

    args = parser.parse_args()
    return args

def display_splash_screen(args: argparse.Namespace) -> None:
    ASCIIColors.cyan(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                   🚀 MOSS Server v{core_version}                      ║
    ║          Fast, Lightweight RAG Server Implementation         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    ASCIIColors.magenta("\n📡 Server Configuration:")
    ASCIIColors.white("    ├─ Host: ", end="")
    ASCIIColors.yellow(f"{args.host}")
    ASCIIColors.white("    ├─ Port: ", end="")
    ASCIIColors.yellow(f"{args.port}")
    ASCIIColors.white("    ├─ LLMModel: ", end="")
    ASCIIColors.yellow(f"{settings.LLM_MODEL}")
    ASCIIColors.white("    ├─ LLMModelName: ", end="")
    ASCIIColors.yellow(f"{settings.LLM_MODEL_NAME}")
    ASCIIColors.white("    ├─ LLMModelHost: ", end="")
    ASCIIColors.yellow(f"{settings.LLM_MODEL_HOST}")
    ASCIIColors.white("    ├─ LLMModelAPIKey: ", end="")
    ASCIIColors.yellow(f"{settings.LLM_MODEL_API_KEY}")
    ASCIIColors.white("    ├─ LightRAGLLMModel: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL}")
    ASCIIColors.white("    ├─ LightRAGLLMModelName: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL_NAME}")
    ASCIIColors.white("    ├─ LightRAGLLMModelMaxTokenSize: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL_MAX_TOKEN_SIZE}")
    ASCIIColors.white("    ├─ LightRAGLLMModelMaxAsync: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL_MAX_ASYNC}")
    ASCIIColors.white("    ├─ LightRAGLLMModelHost: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL_HOST}")
    ASCIIColors.white("    ├─ LightRAGLLMModelAPIKey: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL_API_KEY}")
    ASCIIColors.white("    ├─ LightRAGLLMModelTemperature: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL_TEMPERATURE}")
    ASCIIColors.white("    ├─ LightRAGLLMModelPromptTemplate: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_LLM_MODEL_PROMPT_TEMPLATE}")
    ASCIIColors.white("    ├─ LightRAGEmbedModel: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_EMBED_MODEL}")
    ASCIIColors.white("    ├─ LightRAGEmbedModelName: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_EMBED_MODEL_NAME}")
    ASCIIColors.white("    ├─ LightRAGEmbedModelDim: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_EMBED_MODEL_DIM}")
    ASCIIColors.white("    ├─ LightRAGEmbedModelMaxTokenSize: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_EMBED_MODEL_MAX_TOKEN_SIZE}")
    ASCIIColors.white("    ├─ LightRAGEmbedModelHost: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_EMBED_MODEL_HOST}")
    ASCIIColors.white("    ├─ LightRAGEmbedModelAPIKey: ", end="")
    ASCIIColors.yellow(f"{settings.LIGHTRAG_EMBED_MODEL_API_KEY}")