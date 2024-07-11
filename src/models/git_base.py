from transformers import AutoProcessor, AutoModelForCausalLM, GitConfig, BertTokenizerFast, GitProcessor, AutoTokenizer, CLIPImageProcessor, PreTrainedTokenizerFast
import torch
import random
import numpy as np
from transformers.modeling_outputs import CausalLMOutputWithPast

from torch import nn

from tokenizers import Tokenizer
from typing import List, Optional, Tuple, Union

from transformers.modeling_outputs import BaseModelOutput

from transformers import GitForCausalLM



# processor = AutoProcessor.from_pretrained("microsoft/git-base-coco")
# model = AutoModelForCausalLM.from_pretrained("microsoft/git-base-coco")

# url = "https://cdn.mos.cms.futurecdn.net/YMa7Wx2FyjQFUjEeqa72Rm-1200-80.jpg"
# image = Image.open(requests.get(url, stream=True).raw)

# pixel_values = processor(images=image, return_tensors="pt").pixel_values

# generated_ids = model.generate(pixel_values=pixel_values, max_length=50)
# generated_caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
# print(generated_caption)


class BabyGitModel(nn.Module):
    
    def __init__(self, args=None, use_cuda=False, cuda_device=-1, wandb_object=None, manual_seed=22, use_dino_embeds=False):

        super(BabyGitModel, self).__init__()
        # Initialize the class attributes here
        torch.manual_seed(22)
    
        # random.seed(manual_seed)
        # np.random.seed(manual_seed)
        # torch.manual_seed(manual_seed)
        # # Also setting deterministic behaviour for cudnn.
        # torch.backends.cudnn.deterministic = True
        # torch.use_deterministic_algorithms(True)
        # # torch.set_deterministic(True)
        # torch.cuda.manual_seed_all(manual_seed)
                
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")


        # self.processor = AutoProcessor.from_pretrained("microsoft/git-base-coco")


        self.clip_image_processor = CLIPImageProcessor()
        # clip image processor should be ok because its just cropping and transforming the image without a learned network

        # self.tokenizer = AutoTokenizer.from_pretrained("microsoft/git-base-coco")

        tokenizer_path =  "./src/tokenizer/multi_50m_and_captions_tokenizer_bpe.json"

        self.tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path, padding_side='left')

        self.tokenizer.add_special_tokens(
            {
                'pad_token': '<pad>',
                'sep_token': '<s>',
                'eos_token': '</s>'
             }
            )
        # GIT needs predefined pad token

        self.processor = GitProcessor(self.clip_image_processor, self.tokenizer)


        # self.model = AutoModelForCausalLM.from_pretrained("microsoft/git-base-coco")

        print('-- INITING MODEL FROM SCRATCH -- ')

        git_config = GitConfig()

        self.model: GitForCausalLM = AutoModelForCausalLM.from_config(git_config)

        if use_dino_embeds:
            self.model.git.image_encoder = IdentityVisionModel()

            self.model.git.encoder.layer[0].attention.self.image_patch_tokens = 1

        
        
        # Train a tokenizer.
        # Image processor need not be trained because all it does is apply transformations to the image.
        
        
        # Load a randomly initialized model here.
        # Make sure that the format is of AutoModelForSequenceClassification or AutoModelForCausalLM

    def forward(self, pixel_values=None, input_ids=None, attention_mask=None) -> CausalLMOutputWithPast:

        # CausalLMOutputWithPast is the direct output of the GitModel (which inherits from AutoModelForCausalLM, which is required by eval of babylm)

        # pixel_values = self.processor(images=image, return_tensors="pt").pixel_values

        # convert images to pixel values in dataloader ig

        if pixel_values == None:
            model_outputs: CausalLMOutputWithPast = self.model(input_ids=input_ids, labels=input_ids, attention_mask=attention_mask)
            

        

        model_outputs: CausalLMOutputWithPast = self.model(input_ids=input_ids, pixel_values=pixel_values, labels=input_ids, attention_mask=attention_mask)

        return model_outputs

        
        
        
    # def train(self, train_dataloader, val_dataloader, method='random', pacing='gaussian', t_total=1000):
    #     pass


class IdentityVisionModel(nn.Module):
    def __init__(self):
        super(IdentityVisionModel, self).__init__()



    def forward(
        self,
        pixel_values: Optional[torch.FloatTensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, BaseModelOutput]:

        '''
        Identity forward
        '''

        # pixel_values is of rank 4. 
        # dino embeddings input in pixel_values would be of shape (1, 1, batch_size, 768)

        outputs = pixel_values[0, 0, :, :]

        # need outputs shape to be (batch_size, 1, 768)

        outputs = outputs.unsqueeze(1)

        # print('outputs shape ', outputs.shape)
        return BaseModelOutput(
            last_hidden_state=outputs,
            hidden_states=None,
            attentions=None,
        )






        
