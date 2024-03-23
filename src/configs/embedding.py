model_name = "intfloat/multilingual-e5-large-instruct"
collection_name = "bolosophy_new"
summarizer_api_base = {
    'en': 'https://openrouter.ai/api/v1',
    'cn': 'https://openrouter.ai/api/v1'
}
summarizer_model_name = {
    # 'en': 'meta-llama/llama-3.2-3b-instruct',
    'en': 'google/gemini-flash-1.5-8b',
    # 'cn': 'openai/gpt-4o-mini'
    'cn': 'qwen/qwen-2-7b-instruct'
}
chunk_size = {
    'en': 1500,
    'cn': 500
}
summarizer_template = {
    'en': "Please give a title for this passage, no need to explain the meaning of the title: {context}.\nMy title:",
    'cn': "请为这段话起一个概括性的标题，不需要解释标题含义: {context}。\n我的标题："
}