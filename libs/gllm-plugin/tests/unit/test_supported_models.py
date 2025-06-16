import base64

import pytest

from gllm_plugin.supported_models import BEDROCK_REGION_PREFIXES, ModelName, Provider


def test_invalid_model_name_for_provider() -> None:
    """
    Condition:
    Attempt to create a ModelName with an invalid model name for a provider.

    Expected:
    Should raise ValueError with appropriate error message containing valid models.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName(provider=Provider.OPENAI, name="invalid-model", version=None)

    assert "Invalid model name" in str(exc_info.value)
    assert "Valid models are:" in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_string",
    [
        "openai",
        "openai_gpt-4o",
        "",
    ],
)
def test_from_string_invalid_format(invalid_string: str) -> None:
    """
    Condition:
    Attempt to create a ModelName from various invalid string formats.

    Expected:
    Should raise ValueError with message about invalid format.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName.from_string(invalid_string)

    assert "Invalid format" in str(exc_info.value)
    assert "Expected 'provider/model-name[-version]'" in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_string",
    ["invalid-provider/gpt-4o", "/gpt-4o"],
)
def test_from_string_invalid_provider(invalid_string: str) -> None:
    """
    Condition:
    Attempt to create a ModelName from a string with invalid provider.

    Expected:
    Should raise ValueError with message about invalid provider.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName.from_string(invalid_string)

    assert "Invalid provider" in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_string",
    ["openai/invalid-model", "openai/"],
)
def test_from_string_invalid_model(invalid_string: str) -> None:
    """
    Condition:
    Attempt to create a ModelName from a string with valid provider but invalid model.

    Expected:
    Should raise ValueError with message about invalid model name.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName.from_string(invalid_string)

    assert "Could not match model name" in str(exc_info.value)
    assert "Valid models are:" in str(exc_info.value)


@pytest.mark.parametrize(
    "input_str,expected_provider,expected_model,expected_version",
    [
        ("openai/gpt-4o", Provider.OPENAI, "gpt-4o", None),
        ("anthropic/claude-3-opus", Provider.ANTHROPIC, "claude-3-opus", "latest"),
        ("google/gemini-1.5-pro", Provider.GOOGLE, "gemini-1.5-pro", "latest"),
        ("anthropic/claude-3-opus-v1", Provider.ANTHROPIC, "claude-3-opus", "v1"),
        ("openai/gpt-4o-0125", Provider.OPENAI, "gpt-4o", "0125"),
        ("google/gemini-1.5-pro-preview", Provider.GOOGLE, "gemini-1.5-pro", "preview"),
        ("openai/gpt-4o-mini", Provider.OPENAI, "gpt-4o-mini", None),
        ("openai/gpt-4o-mini-0125", Provider.OPENAI, "gpt-4o-mini", "0125"),
        # Bedrock models without region prefix
        ("bedrock/mistral.mistral-7b-instruct", Provider.BEDROCK, "mistral.mistral-7b-instruct", "v1:0"),
        ("bedrock/meta.llama4-maverick-17b-instruct", Provider.BEDROCK, "meta.llama4-maverick-17b-instruct", "v1:0"),
        ("bedrock/cohere.embed-multilingual", Provider.BEDROCK, "cohere.embed-multilingual", "v1:0"),
        # Bedrock models with explicit version
        ("bedrock/mistral.mistral-7b-instruct-v0:2", Provider.BEDROCK, "mistral.mistral-7b-instruct", "v0:2"),
        # Bedrock models with region prefix
        ("bedrock/us.meta.llama4-maverick-17b-instruct", Provider.BEDROCK, "meta.llama4-maverick-17b-instruct", "v1:0"),
        ("bedrock/eu.cohere.embed-multilingual", Provider.BEDROCK, "cohere.embed-multilingual", "v1:0"),
        ("bedrock/ap.mistral.mistral-7b-instruct", Provider.BEDROCK, "mistral.mistral-7b-instruct", "v1:0"),
        # Bedrock models with region prefix and explicit version
        (
            "bedrock/us.meta.llama4-maverick-17b-instruct-v1:0",
            Provider.BEDROCK,
            "meta.llama4-maverick-17b-instruct",
            "v1:0",
        ),
        ("bedrock/eu.cohere.embed-multilingual-v3", Provider.BEDROCK, "cohere.embed-multilingual", "v3"),
    ],
)
def test_from_string_valid_cases(
    input_str: str,
    expected_provider: Provider,
    expected_model: str,
    expected_version: str | None,
) -> None:
    """
    Condition:
    Parse various valid model strings with different version formats, including subset model names.

    Expected:
    Should correctly parse provider, model name, and version (if present), handling cases where
    one model name is a subset of another (e.g., 'gpt-4o' vs 'gpt-4o-mini').
    """
    model = ModelName.from_string(input_str)
    assert model.provider == expected_provider
    assert model.name == expected_model
    assert model.version == expected_version


@pytest.mark.parametrize(
    "model_name,provider,version,expected_str",
    [
        ("gpt-4o", Provider.OPENAI, None, "openai/gpt-4o"),
        ("claude-3-opus", Provider.ANTHROPIC, "latest", "anthropic/claude-3-opus-latest"),
        ("gemini-1.5-pro", Provider.GOOGLE, "preview", "google/gemini-1.5-pro-preview"),
        ("mistral.mistral-7b-instruct", Provider.BEDROCK, "v1:0", "bedrock/mistral.mistral-7b-instruct-v1:0"),
    ],
)
def test_to_string(model_name: str, provider: Provider, version: str | None, expected_str: str) -> None:
    """
    Condition:
    Create ModelName instances with different versions and convert them to strings.

    Expected:
    Should correctly format the string representation including version if present.
    """
    model = ModelName(provider=provider, name=model_name, version=version)
    assert str(model) == expected_str
    assert model.to_string() == expected_str


@pytest.mark.parametrize(
    "model_name,provider,version,expected_name",
    [
        ("gpt-4o", Provider.OPENAI, None, "gpt-4o"),
        ("claude-3-opus", Provider.ANTHROPIC, "latest", "claude-3-opus-latest"),
        ("gemini-1.5-pro", Provider.GOOGLE, "preview", "gemini-1.5-pro-preview"),
        ("mistral.mistral-7b-instruct", Provider.BEDROCK, "v1:0", "mistral.mistral-7b-instruct-v1:0"),
    ],
)
def test_get_full_name(model_name: str, provider: Provider, version: str | None, expected_name: str) -> None:
    """
    Condition:
    Create ModelName instances with different versions and get their full names.

    Expected:
    Should return the complete model name with version if present.
    """
    model = ModelName(provider=provider, name=model_name, version=version)
    assert model.get_full_name() == expected_name


@pytest.mark.parametrize(
    "invalid_string",
    [
        "openai/invalid-model-0125",  # Invalid model with version
        "anthropic/claude-3-invalid",  # Partial match but invalid model
        "google/gemini-invalid-pro",  # Invalid model between valid parts
    ],
)
def test_from_string_invalid_model_with_version(invalid_string: str) -> None:
    """
    Condition:
    Attempt to create a ModelName from a string with valid provider but invalid model, including version-like parts.

    Expected:
    Should raise ValueError with message about invalid model name.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName.from_string(invalid_string)

    assert "Could not match model name" in str(exc_info.value)
    assert "Valid models are:" in str(exc_info.value)


@pytest.mark.parametrize(
    "url,encoded_url",
    [
        ("https://example.com/model", "aHR0cHM6Ly9leGFtcGxlLmNvbS9tb2RlbA=="),
        ("http://localhost:8080/models/llama", "aHR0cDovL2xvY2FsaG9zdDo4MDgwL21vZGVscy9sbGFtYQ=="),
    ],
)
def test_tgi_model_handling(url: str, encoded_url: str) -> None:
    """
    Condition:
    Create and manipulate ModelName instances for TGI-hosted models using base64-encoded URLs.

    Expected:
    - Should correctly decode base64 URL when creating from string
    - Should store decoded URL as name
    - Should return encoded URL in get_full_name
    - Should correctly reconstruct the model string
    """
    # Test creation from string
    model = ModelName.from_string(f"tgi/{encoded_url}")
    assert model.provider == Provider.TGI
    assert model.name == url
    assert model.version is None
    assert str(model.url) == url

    # Test get_full_name returns encoded URL
    assert model.get_full_name() == encoded_url

    # Test string representation
    assert str(model) == f"tgi/{encoded_url}"
    assert model.to_string() == f"tgi/{encoded_url}"

    # Test direct creation
    direct_model = ModelName(provider=Provider.TGI, name=url, version=None)
    assert direct_model.name == url
    assert direct_model.get_full_name() == encoded_url


@pytest.mark.parametrize(
    "model_name,url,encoded_url",
    [
        ("llama2-7b", "https://example.com/model", "aHR0cHM6Ly9leGFtcGxlLmNvbS9tb2RlbA=="),
        ("mistral-7b", "http://localhost:8080/models/mistral", "aHR0cDovL2xvY2FsaG9zdDo4MDgwL21vZGVscy9taXN0cmFs"),
    ],
)
def test_vllm_model_handling(model_name: str, url: str, encoded_url: str) -> None:
    """
    Condition:
    Create and manipulate ModelName instances for VLLM-hosted models using model name and base64-encoded URLs.

    Expected:
    - Should correctly parse model name and decode base64 URL when creating from string
    - Should store model name and URL separately
    - Should correctly format model string with encoded URL
    - Should correctly reconstruct the model string
    """
    # Test creation from string
    model = ModelName.from_string(f"vllm/{model_name}@{encoded_url}")
    assert model.provider == Provider.VLLM
    assert model.name == model_name
    assert model.version is None
    assert str(model.url) == url

    # Test get_full_name returns model@encoded_url format
    assert model.get_full_name() == f"{model_name}@{encoded_url}"

    # Test string representation
    assert str(model) == f"vllm/{model_name}@{encoded_url}"
    assert model.to_string() == f"vllm/{model_name}@{encoded_url}"

    # Test direct creation
    direct_model = ModelName(provider=Provider.VLLM, name=model_name, url=url)
    assert direct_model.name == model_name
    assert str(direct_model.url) == url
    assert direct_model.get_full_name() == f"{model_name}@{encoded_url}"


@pytest.mark.parametrize(
    "invalid_input",
    [
        "not-base64-encoded",  # Invalid base64
        base64.b64encode(b"not-a-url").decode(),  # Valid base64 but invalid URL
        base64.b64encode(b"invalid-scheme://example.com").decode(),  # Invalid URL scheme
    ],
)
def test_tgi_model_invalid_inputs(invalid_input: str) -> None:
    """
    Condition:
    Attempt to create TGI ModelName instances with invalid inputs.

    Expected:
    Should raise ValueError for invalid base64 encoding or invalid URLs.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName.from_string(f"tgi/{invalid_input}")

    assert "Invalid base64-encoded URL" in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_input",
    [
        "model-name-without-url",  # Missing URL part
        "model@not-base64-encoded",  # Invalid base64
        f"model@{base64.b64encode(b'not-a-url').decode()}",  # Valid base64 but invalid URL format
    ],
)
def test_vllm_model_invalid_inputs(invalid_input: str) -> None:
    """
    Condition:
    Attempt to create VLLM ModelName instances with invalid inputs.

    Expected:
    Should raise ValueError for missing URL, invalid base64 encoding, or invalid URL format.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName.from_string(f"vllm/{invalid_input}")

    error_msg = str(exc_info.value)
    assert any(
        msg in error_msg
        for msg in [
            "Invalid format for vllm model",
            "Invalid base64-encoded URL",
        ]
    )


def test_vllm_model_missing_url() -> None:
    """
    Condition:
    Attempt to get_full_name for a VLLM model without a URL.

    Expected:
    Should raise ValueError indicating URL is required.
    """
    model = ModelName(provider=Provider.VLLM, name="llama2-7b")
    with pytest.raises(ValueError) as exc_info:
        model.get_full_name()

    assert "URL is required for vllm models" in str(exc_info.value)


@pytest.mark.parametrize(
    "prefix,expected_result",
    [
        ("us", True),
        ("eu", True),
        ("ap", True),
        ("invalid", False),
        ("usa", False),
        ("EUR", False),
    ],
)
def test_bedrock_region_prefixes(prefix: str, expected_result: bool) -> None:
    """
    Condition:
    Check if a string is a valid Bedrock region prefix.

    Expected:
    Should return True for valid prefixes (us, eu, ap) and False for invalid ones.
    """
    assert (prefix in BEDROCK_REGION_PREFIXES) == expected_result


@pytest.mark.parametrize(
    "model_string",
    [
        "bedrock/invalid.model",  # Invalid model name
        "bedrock/unknown.mistral-7b-instruct",  # Invalid prefix (not a region)
    ],
)
def test_bedrock_invalid_model(model_string: str) -> None:
    """
    Condition:
    Attempt to create a ModelName from a string with valid provider but invalid Bedrock model.

    Expected:
    Should raise ValueError with message about invalid model name.
    """
    with pytest.raises(ValueError) as exc_info:
        ModelName.from_string(model_string)

    assert "Could not match model name" in str(exc_info.value) or "Invalid model name" in str(exc_info.value)


@pytest.mark.parametrize(
    "model_name,prefix,version,expected_full_name",
    [
        ("mistral.mistral-7b-instruct", None, "v1:0", "mistral.mistral-7b-instruct-v1:0"),
        ("meta.llama4-maverick-17b-instruct", "us", "v1:0", "us.meta.llama4-maverick-17b-instruct-v1:0"),
        ("cohere.embed-multilingual", "eu", "v3", "eu.cohere.embed-multilingual-v3"),
        ("anthropic.claude-3-5-sonnet", "ap", None, "ap.anthropic.claude-3-5-sonnet-v1:0"),  # Default version
    ],
)
def test_bedrock_get_full_name(model_name: str, prefix: str, version: str, expected_full_name: str) -> None:
    """
    Condition:
    Create Bedrock ModelName instances with different prefixes and versions and get their full names.

    Expected:
    Should return the complete model name with prefix and version correctly formatted.
    """
    model = ModelName(provider=Provider.BEDROCK, name=model_name, prefix=prefix, version=version)
    assert model.get_full_name() == expected_full_name


@pytest.mark.parametrize(
    "input_str,expected_provider,expected_prefix,expected_model,expected_version",
    [
        ("bedrock/mistral.mistral-7b-instruct", Provider.BEDROCK, None, "mistral.mistral-7b-instruct", "v1:0"),
        (
            "bedrock/us.meta.llama4-maverick-17b-instruct-v1:0",
            Provider.BEDROCK,
            "us",
            "meta.llama4-maverick-17b-instruct",
            "v1:0",
        ),
        ("bedrock/eu.cohere.embed-multilingual-v3", Provider.BEDROCK, "eu", "cohere.embed-multilingual", "v3"),
        ("bedrock/ap.mistral.mistral-7b-instruct", Provider.BEDROCK, "ap", "mistral.mistral-7b-instruct", "v1:0"),
    ],
)
def test_bedrock_from_string_with_prefix(
    input_str: str,
    expected_provider: Provider,
    expected_prefix: str,
    expected_model: str,
    expected_version: str,
) -> None:
    """
    Condition:
    Parse various valid Bedrock model strings with different region prefixes and versions.

    Expected:
    Should correctly parse provider, region prefix, model name, and version.
    """
    model = ModelName.from_string(input_str)
    assert model.provider == expected_provider
    assert model.prefix == expected_prefix
    assert model.name == expected_model
    assert model.version == expected_version
