"""Defines the supported models for the pipeline.

Authors:
    Dimitrij Ray (dimitrij.ray@gdplabs.id)

References:
    NONE
"""

import base64
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, HttpUrl, ValidationError


class Provider(StrEnum):
    """Supported model providers."""

    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure-openai"
    DEEPSEEK = "deepseek"
    GOOGLE = "google"
    OPENAI = "openai"
    TGI = "tgi"
    TEI = "tei"
    VLLM = "vllm"
    GROQ = "groq"
    TOGETHER_AI = "together-ai"
    DEEPINFRA = "deepinfra"
    VOYAGE = "voyage"

    ROUTABLE = "routable"


class OpenAIModel(StrEnum):
    """Supported OpenAI models."""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_5_PREVIEW = "gpt-4.5-preview"
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"
    O1 = "o1"
    O1_MINI = "o1-mini"
    O1_PREVIEW = "o1-preview"
    O3 = "o3"
    O3_MINI = "o3-mini"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


class AzureOpenAIModel(StrEnum):
    """Supported Azure OpenAI models."""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"


class AnthropicModel(StrEnum):
    """Supported Anthropic models."""

    CLAUDE_3_7_SONNET = "claude-3-7-sonnet"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku"
    CLAUDE_3_OPUS = "claude-3-opus"


class GoogleModel(StrEnum):
    """Supported Google models."""

    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_FLASH_8B = "gemini-1.5-flash-8b"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    TEXT_EMBEDDING_GECKO_001 = "textembedding-gecko@001"
    TEXT_EMBEDDING_GECKO_003 = "textembedding-gecko@003"
    TEXT_EMBEDDING_004 = "text-embedding-004"
    TEXT_EMBEDDING_005 = "text-embedding-005"


class DeepSeekModel(StrEnum):
    """Supported DeepSeek models."""

    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_REASONER = "deepseek-reasoner"


class GroqModel(StrEnum):
    """Supported Groq models."""

    DEEPSEEK_R1_DISTILL_QWEN_32B = "deepseek-r1-distill-qwen-32b"
    DEEPSEEK_R1_DISTILL_LLAMA_70B = "deepseek-r1-distill-llama-70b"
    LLAMA_3_2_1B_PREVIEW = "llama-3.2-1b-preview"


class TogetherAIModel(StrEnum):
    """Supported Together.AI models."""

    DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3"


class DeepInfraModel(StrEnum):
    """Supported DeepInfra models."""

    QWEN_2_5_72B_INSTRUCT = "Qwen/Qwen2.5-72B-Instruct"
    DEEPSEEK_R1_DISTILL_QWEN_32B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    DEEPSEEK_R1 = "deepseek-ai/DeepSeek-R1"
    DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3"


class VoyageModel(StrEnum):
    """Supported Voyage models."""

    VOYAGE_3_LARGE = "voyage-3-large"
    VOYAGE_3 = "voyage-3"
    VOYAGE_3_LITE = "voyage-3-lite"
    VOYAGE_CODE_3 = "voyage-code-3"
    VOYAGE_FINANCE_2 = "voyage-finance-2"
    VOYAGE_LAW_2 = "voyage-law-2"
    VOYAGE_CODE_2 = "voyage-code-2"


class RoutableModel(StrEnum):
    """Supported routable model presets.

    These are presets that map a specific model name to a routable invoker.
    The actual invoker will be determined by the router.

    Currently supports:
        - '__default__' - Strong model: gpt-4o. Weak model: gpt-4o-mini.
        - 'gpt' - Strong model: o3-mini. Weak model: gpt-4o.
        - 'deepseek' - Strong model: DeepSeek-R1-Distill-Qwen-32B. Weak model: DeepSeek-V3.
    """

    DEFAULT = "__default__"
    GPT = "gpt"
    DEEPSEEK = "deepseek"


MODEL_MAP = {
    Provider.OPENAI: OpenAIModel,
    Provider.ANTHROPIC: AnthropicModel,
    Provider.GOOGLE: GoogleModel,
    Provider.DEEPSEEK: DeepSeekModel,
    Provider.GROQ: GroqModel,
    Provider.TOGETHER_AI: TogetherAIModel,
    Provider.DEEPINFRA: DeepInfraModel,
    Provider.ROUTABLE: RoutableModel,
    Provider.VOYAGE: VoyageModel,
    Provider.AZURE_OPENAI: AzureOpenAIModel,
}

DEFAULT_VERSION_MAP = {
    Provider.OPENAI: None,
    Provider.ANTHROPIC: "latest",
    Provider.GOOGLE: "latest",
    Provider.TGI: None,
    Provider.TEI: None,
    Provider.VLLM: None,
    Provider.DEEPSEEK: None,
    Provider.GROQ: None,
    Provider.TOGETHER_AI: None,
    Provider.DEEPINFRA: None,
    Provider.ROUTABLE: None,
    Provider.VOYAGE: None,
    Provider.AZURE_OPENAI: None,
}

UNIMODAL_PROVIDERS = {Provider.TGI, Provider.VLLM}
UNIMODAL_MODELS = {
    DeepInfraModel.DEEPSEEK_R1,
    DeepInfraModel.DEEPSEEK_R1_DISTILL_QWEN_32B,
    DeepInfraModel.DEEPSEEK_V3,
    DeepInfraModel.QWEN_2_5_72B_INSTRUCT,
    RoutableModel.DEEPSEEK,
    DeepSeekModel.DEEPSEEK_CHAT,
    DeepSeekModel.DEEPSEEK_REASONER,
    GroqModel.DEEPSEEK_R1_DISTILL_QWEN_32B,
    GroqModel.DEEPSEEK_R1_DISTILL_LLAMA_70B,
    GroqModel.LLAMA_3_2_1B_PREVIEW,
    TogetherAIModel.DEEPSEEK_V3,
}


def validate_model_name(model_name: str, provider: Provider) -> str:
    """A Pydantic validator that validates the model name is valid for the given provider.

    Args:
        model_name (str): The model name to validate.
        provider (Provider): The provider to validate the model name against.

    Returns:
        str: The validated model name.

    Raises:
        ValueError: If the model name is invalid for the provider.
    """
    if provider in {Provider.TGI, Provider.TEI}:
        try:
            HttpUrl(model_name)
            return model_name
        except ValidationError as e:
            raise ValueError(f"Invalid URL for TGI provider: {str(e)}") from e

    if provider == Provider.VLLM:
        if not model_name:
            raise ValueError("Model name cannot be empty for VLLM provider")
        return model_name

    model_enum = MODEL_MAP[provider]
    valid_models = [m.value for m in model_enum]

    if model_name not in valid_models:
        valid_models_str = ", ".join(valid_models)
        raise ValueError(
            f'Invalid model name "{model_name}" for provider "{provider}". ' f"Valid models are: {valid_models_str}"
        )
    return model_name


class ModelName(BaseModel):
    """A model name in a standardized format.

    - For cloud providers: 'provider/model-name[-version]'
    - For TGI: 'tgi/[base64-encoded-url]'
    - For VLLM: 'vllm/[model-name]@[base64-encoded-url]'

    Args:
        provider (Provider): The provider of the model.
        name (str): The name of the model.
        version (str | None, optional): The version of the model. Defaults to None.
        url (HttpUrl | None, optional): The URL for self-hosted models (e.g. TGI, VLLM). Defaults to None.

    Attributes:
        provider (Provider): The provider of the model.
        name (str): The name of the model.
        version (str | None): The version of the model.
        url (HttpUrl | None): The URL for self-hosted models (e.g. TGI, VLLM).

    Raises:
        ValueError: If the model name is invalid for the provider.
    """

    model_config = ConfigDict(frozen=True)

    provider: Provider
    name: Annotated[
        str,
        BeforeValidator(lambda v, info: validate_model_name(v, info.data.get("provider"))),
    ]
    version: Annotated[
        str | None,
        BeforeValidator(lambda v, info: (DEFAULT_VERSION_MAP[info.data.get("provider")] if v is None else v)),
    ] = None
    url: HttpUrl | None = None

    @classmethod
    def from_string(cls, provider_model_string: str) -> "ModelName":
        """Parse a provider/model string into a ModelName.

        Format varies by provider:
        - Cloud providers: 'provider/model-name[-version]'
        - TGI: 'tgi/[base64-encoded-url]'
        - TEI: 'tei/[base64-encoded-url]'
        - VLLM: 'vllm/[model-name]@[base64-encoded-url]'

        Args:
            provider_model_string (str): The provider/model string.

        Returns:
            ModelName: The parsed model name.

        Raises:
            ValueError: If the string format is invalid or the provider is not supported.
        """
        try:
            provider_str, model_str = provider_model_string.split("/", 1)
        except ValueError as err:
            raise ValueError("Invalid format. Expected 'provider/model-name[-version]'") from err

        try:
            provider = Provider(provider_str)
        except ValueError as err:
            raise ValueError(f"Invalid provider '{provider_str}'") from err

        if provider in {Provider.TGI, Provider.TEI}:
            try:
                decoded_url = base64.b64decode(model_str).decode()
                HttpUrl(decoded_url)
                return cls(provider=provider, name=decoded_url, url=decoded_url)
            except (ValidationError, UnicodeDecodeError) as e:
                raise ValueError(f"Invalid base64-encoded URL: {str(e)}") from e

        if provider == Provider.VLLM:
            if "@" not in model_str:
                raise ValueError("Invalid format for VLLM model. Expected: vllm/model-name@base64-encoded-url")

            model_name, encoded_url = model_str.split("@", 1)
            try:
                decoded_url = base64.b64decode(encoded_url).decode()
                return cls(provider=provider, name=model_name, url=decoded_url)
            except Exception as e:
                raise ValueError(f"Invalid base64-encoded URL: {str(e)}") from e

        model_enum = MODEL_MAP[provider]
        matching_model = None
        version = None

        sorted_models = sorted(model_enum, key=lambda x: len(x.value), reverse=True)

        for model in sorted_models:
            if model_str.startswith(model.value):
                matching_model = model.value
                remaining = model_str[len(model.value) :].lstrip("-")
                version = remaining if remaining else DEFAULT_VERSION_MAP[provider]
                break

        if matching_model is None:
            valid_models = ", ".join([m.value for m in model_enum])
            raise ValueError(
                f'Could not match model name "{model_str}" for provider "{provider}". '
                f"Valid models are: {valid_models}"
            )

        return cls(provider=provider, name=matching_model, version=version)

    def __str__(self) -> str:
        """Return the standard provider/model[-version] format as a string.

        Returns:
            str: The standard provider/model[-version] format as a string.
        """
        return self.to_string()

    def to_string(self) -> str:
        """Return the standard format as a string.

        Returns:
            str: The formatted string representation.
        """
        return f"{self.provider}/{self.get_full_name()}"

    def get_full_name(self) -> str:
        """Return the complete model identifier.

        For cloud providers: name[-version]
        For TGI: base64-encoded-url
        For TEI: base64-encoded-url
        For VLLM: model-name@base64-encoded-url

        Returns:
            str: The complete model identifier.

        Raises:
            ValueError: If URL is required but not provided, or if URL is invalid.
        """
        if self.provider in {Provider.TGI, Provider.TEI}:
            return base64.b64encode(self.name.encode()).decode()

        if self.provider == Provider.VLLM:
            if not self.url:
                raise ValueError("URL is required for VLLM models")
            encoded_url = base64.b64encode(str(self.url).encode()).decode()
            return f"{self.name}@{encoded_url}"

        if self.version:
            return f"{self.name}-{self.version}"
        return self.name
