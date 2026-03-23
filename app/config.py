import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    app_mode: str = os.getenv("APP_MODE", "rule").strip().lower()
    model_provider: str = os.getenv("MODEL_PROVIDER", "glm").strip().lower()

    glm_api_key: str = os.getenv("GLM_API_KEY", "").strip()
    glm_base_url: str = os.getenv(
        "GLM_BASE_URL",
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    ).strip()
    glm_model: str = os.getenv("GLM_MODEL", "glm-4.7").strip()

    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "").strip()
    deepseek_base_url: str = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com/chat/completions",
    ).strip()
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner").strip()

    llm_timeout: int = int(os.getenv("LLM_TIMEOUT", "120"))
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    def validate(self):
        if self.app_mode not in {"rule", "llm"}:
            raise ValueError("APP_MODE 只能是 rule 或 llm")
        if self.model_provider not in {"glm", "deepseek"}:
            raise ValueError("MODEL_PROVIDER 只能是 glm 或 deepseek")

    @property
    def llm_enabled(self) -> bool:
        if self.app_mode != "llm":
            return False
        if self.model_provider == "glm":
            return bool(self.glm_api_key)
        if self.model_provider == "deepseek":
            return bool(self.deepseek_api_key)
        return False

    @property
    def effective_mode(self) -> str:
        return "llm" if self.llm_enabled else "rule"

    def provider_config(self):
        if self.model_provider == "glm":
            return {
                "api_key": self.glm_api_key,
                "base_url": self.glm_base_url,
                "model": self.glm_model,
            }
        return {
            "api_key": self.deepseek_api_key,
            "base_url": self.deepseek_base_url,
            "model": self.deepseek_model,
        }

    def startup_note(self) -> str:
        if self.app_mode == "llm" and not self.llm_enabled:
            return "检测到 APP_MODE=llm，但没有可用 API Key，系统已自动回退到 rule 模式。"
        return "配置加载成功。"


settings = Settings()
