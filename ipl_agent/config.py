import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    GOOGLE = "google"
    GROQ = "GROQ"


@dataclass
class ModelConfig:
    name: str
    temperature: float
    provider: ModelProvider


LLAMA3 = ModelConfig("llama3.2:3b", 0.0, ModelProvider.OLLAMA)
GEMINI_FLASH = ModelConfig("gemini-2.5-flash-lite", 0.3, ModelProvider.GOOGLE)
LLAMA4_SCOUT = ModelConfig("meta-llama/llama-4-scout-17b-16e-instruct", 0.3, ModelProvider.GROQ)


class Config:
    SEED = 42
    MODEL = GEMINI_FLASH
    OLLAMA_CONTEXT_WINDOW = 2048

    class Path:
        APP_HOME = Path(__file__).parent.parent
        DATA_DIR = APP_HOME / "ipl_dwh"
        DATABASE_PATH = DATA_DIR / "dev.duckdb"

def seed_everything(seed: int = Config.SEED):
    random.seed(seed)
