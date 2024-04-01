import requests

OPENROUTER_MODEL_PRICES = None

def get_model_price(model_name, provider):
    global OPENROUTER_MODEL_PRICES
    if provider in ['OpenRouter', 'OpenAI']:
        if OPENROUTER_MODEL_PRICES is None:
            try:
                # get data from OpenRouter API
                response = requests.get('https://openrouter.ai/api/v1/models')
                response.raise_for_status()  # Raises stored HTTPError, if one occurred.
                response = response.json()
                OPENROUTER_MODEL_PRICES = dict()
                for model_info in response['data']:
                    OPENROUTER_MODEL_PRICES[model_info['id']] = model_info['pricing']
            except requests.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                return None
            except Exception as err:
                print(f'Other error occurred: {err}')
                return None
        if model_name in OPENROUTER_MODEL_PRICES:
            price_dict = OPENROUTER_MODEL_PRICES[model_name]
            # escape for LaTex syntax
            result = {
                'input': f"\\${float(price_dict['prompt'])*1000000:.2f}/M tkns",
                'output': f"\\${float(price_dict['completion'])*1000000:.2f}/M tkns",
            }
            if float(price_dict['image']) > 0:
                result['image'] = f"\\${float(price_dict['image'])*1000:.2f}/K imgs"
            if provider == 'OpenRouter':
                result['your credit'] = '[link](https://openrouter.ai/credits)'
            return result
        return None
    elif provider in ['Qwen', 'Qwen Open Source']:
        # TODO: get data from Qwen API
        return {
            'Price detail': '[link](https://dashscope.console.aliyun.com/billing)',
            'your billing': '[link](https://usercenter2.aliyun.com/home)',
        }
