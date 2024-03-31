from typing import Optional, Type
import requests
import json
import uuid
from datetime import datetime

from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from huggingface_hub import InferenceClient
import streamlit as st

# hf inference client api see https://huggingface.co/docs/huggingface_hub/v0.23.2/package_reference/inference_client#huggingface_hub.InferenceClient.text_to_image

class DrawInput(BaseModel):
    prompt: str = Field(description="Prompt for image generation")
    negative_prompt: Optional[str] = Field(description="An optional negative prompt for the image generation")


class DrawTool(BaseTool):
    name = "Draw"
    description = "Draw an image using diffusion-based models based on the given prompt."
    args_schema: Type[BaseModel] = DrawInput
    return_direct: bool = False
    
    emoji: str = "🎨"
    hf_client: InferenceClient = None
    width: float = 512
    height: float = 512
    model: str = "black-forest-labs/FLUX.1-schnell"
    
    def __init__(self):
        super().__init__()
        self.hf_client = InferenceClient(token=st.secrets['huggingface_key'])

    def _run(
        self, 
        prompt: str, 
        negative_prompt: Optional[str] = None, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        print(f'Draw test with prompt: {prompt} and negative prompt: {negative_prompt}')
        image = self.hf_client.text_to_image(
            prompt,
            negative_prompt=negative_prompt,
            model=self.model,
            height=self.height,
            width=self.width,
        )
        print(f'Image generated with size {image.size}')
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = uuid.uuid4().hex[:6]
        save_path = f'static/{timestamp}_{random_id}.png'
        image.save(save_path)
        return f'The image is generated using prompt: \n\n```\n{prompt}\n```\n\n ![image](app/{save_path})'
        # return json.dumps({'img_url': f'app/{save_path}'}, ensure_ascii=False)

    def st_config(self):
        """config setting in streamlit"""
        self.width = st.slider('Width', 
                            min_value=256,
                            max_value=1024,
                            step=32,
                            value=512,
                            help='''The width in pixels of the image to generate.''')
        self.height = st.slider('Height', 
                            min_value=256,
                            max_value=1024,
                            step=32,
                            value=512,
                            help='''The height in pixels of the image to generate.''')
        self.model = st.selectbox('Model', 
                            [
                                "black-forest-labs/FLUX.1-schnell",
                                "black-forest-labs/FLUX.1-dev",
                                "stabilityai/stable-diffusion-2-1",
                                "stabilityai/stable-diffusion-xl-base-1.0",
                            ],
                            help='The model to use for image generation.')

if __name__ == '__main__':
    tool = DrawTool()
    print(tool.name)
    print(tool.description)
    print(tool.args)
    print(tool.return_direct)

    print(tool.invoke({"prompt": 'draw a cartoon yellow squirrel mouse with a lightning bolt tail'}))