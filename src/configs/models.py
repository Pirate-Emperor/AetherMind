available_models = [
    {
        'group': 'OpenAI',
        'icon': 'https://openai.com/favicon.ico',
        'supports_official_api': True,
        'official_api_base': 'https://api.openai.com/v1',
        'official_api_link': 'https://openai.com/api/',
        'supports_open_router': True,
        'open_router_prefix': 'openai',
        'models': [
            {
                'display_name': 'GPT-4o',
                'api_name': 'gpt-4o-2024-05-13',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'GPT-4o-mini',
                'api_name': 'gpt-4o-mini-2024-07-18',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'GPT-4 Turbo 2024-04-09',
                'api_name': 'gpt-4-turbo',
                'is_free': False,
                'native_tool_support': True,
            }
        ]
    },
    {
        'group': 'Qwen',
        'icon': 'https://img.alicdn.com/imgextra/i4/O1CN01FOwagl1XBpyVA2QVy_!!6000000002886-2-tps-512-512.png',
        'supports_official_api': True,
        'official_api_base': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'official_api_link': 'https://bailian.console.aliyun.com/',
        'supports_open_router': False,
        'open_router_prefix': 'qwen',
        'models': [
            {
                'display_name': 'Qwen2.5 Max 0428',
                'api_name': 'qwen-max-0428',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Qwen Plus',
                'api_name': 'qwen-plus',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Qwen Turbo',
                'api_name': 'qwen-turbo',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Qwen Long',
                'api_name': 'qwen-long',
                'is_free': False,
                'native_tool_support': False,
            },
        ]
    },
    {
        'group': 'Qwen Open Source',
        'icon': 'https://img.alicdn.com/imgextra/i4/O1CN01FOwagl1XBpyVA2QVy_!!6000000002886-2-tps-512-512.png',
        'supports_official_api': True,
        'official_api_base': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'official_api_link': 'https://bailian.console.aliyun.com/',
        'supports_open_router': False,
        'open_router_prefix': 'qwen',
        'models': [
            {
                'display_name': 'Qwen1.5 110B Chat',
                'api_name': 'qwen1.5-110b-chat',
                'is_free': False,
                'native_tool_support': False,
            },
            {
                'display_name': 'Qwen2 72B Instruct',
                'api_name': 'qwen2-72b-instruct',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Qwen1.5 32B Chat',
                'api_name': 'qwen1.5-32b-chat',
                'is_free': False,
                'native_tool_support': False,
            },
            {
                'display_name': 'Qwen2 57B-A14B Instruct',
                'api_name': 'qwen2-57b-a14b-instruct',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Qwen2 7B Instruct',
                'api_name': 'qwen2-72b-instruct',
                'is_free': False,
                'native_tool_support': True,
            },
        ]
    },
    {
        'group': 'Meta Llama',
        'icon': 'https://static.xx.fbcdn.net/rsrc.php/y5/r/m4nf26cLQxS.ico',
        'supports_official_api': False,
        'supports_open_router': True,
        'open_router_prefix': 'meta-llama',
        'models': [
            {
                'display_name': 'Llama 3 8B Instruct (free)',
                'api_name': 'llama-3-8b-instruct:free',
                'is_free': True,
                'native_tool_support': False,
            },
            {
                'display_name': 'Llama 3 70B Instruct',
                'api_name': 'llama-3-70b-instruct',
                'is_free': False,
                'native_tool_support': False,
            },
        ]
    },
    {
        'group': 'Anthropic',
        'icon': 'https://www.anthropic.com/images/icons/apple-touch-icon.png',
        'supports_official_api': False,
        'supports_open_router': True,
        'open_router_prefix': 'anthropic',
        'models': [
            {
                'display_name': 'Claude 3.5 Sonnet',
                'api_name': 'claude-3.5-sonnet',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Claude 3 Opus',
                'api_name': 'claude-3-opus',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Claude 3 Sonnet',
                'api_name': 'claude-3-sonnet',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Claude 3 Haiku',
                'api_name': 'claude-3-haiku',
                'is_free': False,
                'native_tool_support': True,
            },
        ]
    },
    {
        'group': 'Google',
        'icon': 'https://www.google.com/images/branding/googleg/1x/googleg_standard_color_128dp.png',
        'supports_official_api': False,
        'supports_open_router': True,
        'open_router_prefix': 'google',
        'models': [
            {
                'display_name': 'Gemma 7B Instruct (free)',
                'api_name': 'gemma-7b-it:free',
                'is_free': True,
                'native_tool_support': False,
            },
            {
                'display_name': 'Gemini Pro 1.5',
                'api_name': 'gemini-pro-1.5',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Gemini Flash 1.5',
                'api_name': 'gemini-flash-1.5',
                'is_free': False,
                'native_tool_support': True,
            },
            {
                'display_name': 'Gemini Pro 1.0',
                'api_name': 'gemini-pro',
                'is_free': False,
                'native_tool_support': False,
            },
        ]
    },
    {
        'group': 'Microsoft',
        'icon': 'https://c.s-microsoft.com/favicon.ico?v2',
        'supports_official_api': False,
        'supports_open_router': True,
        'open_router_prefix': 'microsoft',
        'models': [
            {
                'display_name': 'Phi 3 Mini 128k Instruct (free)',
                'api_name': 'phi-3-mini-128k-instruct:free',
                'is_free': True,
                'native_tool_support': False,
            },
            {
                'display_name': 'Phi 3 Medium 128k Instruct (free)',
                'api_name': 'phi-3-medium-128k-instruct:free',
                'is_free': True,
                'native_tool_support': False,
            },
        ]
    },
]