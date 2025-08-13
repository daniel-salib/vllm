# @noautodeps

# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

"""
vLLM uses a plugin system based on python packaging metadata to allow users to
add custom user-registered code that vLLM loads and executes at runtime.

See https://docs.vllm.ai/en/latest/design/plugin_system.html for more details

Buck build is set up to produce a entry_points.txt that tells python to add
the register() function as a entry point that belongs to group vllm.general_plugins that
vLLM loads from.
"""


def register():
    import vllm.transformers_utils.configs.eagle as eagle
    from transformers import Llama4Config
    from transformers.models.auto.modeling_auto import (
        MODEL_FOR_CAUSAL_LM_MAPPING_NAMES as CONFIG_MAPPING_NAMES,
    )
    from vllm.inputs.registry import InputContext
    from vllm.transformers_utils.config import _CONFIG_REGISTRY
    from vllm.transformers_utils.configs.configuration_llama4feather import (
        Llama4FeatherConfig,
    )
    from vllm.transformers_utils.configs.eagle import EAGLEConfig

    def get_hf_config(self, *args, **kwargs):
        return self.model_config.hf_config

    # Monkey patch get_hf_config since the raw get_hf_config requires the hf config same type as the transformer hf config
    InputContext.get_hf_config = get_hf_config

    # Monkey patch EAGLEConfig to use fb config compatible
    # with HF officially  generated ckpt (including both text and MM weights and configs) based on
    # https://github.com/huggingface/new-model-addition-llama4-feather/pull/4
    eagle.EAGLEConfig = EAGLEConfig

    # Newest HF checkpoints for llama4 feather models have cache_implementation set to yoco_hybrid_chunked
    # but current /third-party HF version doesn't support yoco_hybrid_chunked as a valid cache type
    # override for now to enable internal testing on vLLM
    # TODO(yhshin): remove override here after feather OSS launch
    from transformers.generation.configuration_utils import (
        ALL_CACHE_IMPLEMENTATIONS,
        NEED_SETUP_CACHE_CLASSES_MAPPING,
    )

    NEED_SETUP_CACHE_CLASSES_MAPPING["yoco_hybrid"] = NEED_SETUP_CACHE_CLASSES_MAPPING[
        "hybrid"
    ]
    NEED_SETUP_CACHE_CLASSES_MAPPING["yoco_hybrid_chunked"] = (
        NEED_SETUP_CACHE_CLASSES_MAPPING["hybrid_chunked"]
    )
    ALL_CACHE_IMPLEMENTATIONS += ["yoco_hybrid", "yoco_hybrid_chunked"]

    _CONFIG_REGISTRY["llama4"] = Llama4Config
    _CONFIG_REGISTRY["llama4feather"] = Llama4FeatherConfig

    from vllm.model_executor.models.llama4_eagle import EagleLlama4ForCausalLM

    from vllm.model_executor.models.mllama4 import (
        Llama4ForCausalLM,
        Llama4ForConditionalGeneration,
    )

    from vllm.model_executor.models.registry import ModelRegistry

    CONFIG_MAPPING_NAMES.update({"llama4feather": "Llama4ForConditionalGeneration"})
    ModelRegistry.register_model("Llama4ForCausalLM", Llama4ForCausalLM)
    ModelRegistry.register_model(
        "Llama4ForConditionalGeneration", Llama4ForConditionalGeneration
    )
    ModelRegistry.register_model(
        "Llama4FeatherForConditionalGeneration", Llama4ForConditionalGeneration
    )
    ModelRegistry.register_model("EagleLlama4ForCausalLM", EagleLlama4ForCausalLM)

    # Use vLLM video loader backend for mllama4
    from vllm import envs

    envs.VLLM_VIDEO_LOADER_BACKEND = "mllama4"
