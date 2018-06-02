"""
author: Caner Mercan
"""

import copy
import torch.nn as nn
from deepnets import convprops as CP

__names__ = 'alexnet', 'vggnet' # currently implemented models

class ConvnetModel(nn.Module):
    def __init__(self, num_classes, name, model):
        super().__init__()
        
        if name.startswith('alex'):
            self.name = CP.MODULE_NAMES[0] # alexnet
            self.features   = model.features
            self.classifier = nn.Sequential(
                nn.Dropout(p = 0.5),
                nn.Linear(256*6*6, 4096), # 9216 -> 4096
                nn.ReLU(inplace = True),
                nn.Dropout(p = 0.5),
                nn.Linear(4096, 4096),
                nn.ReLU(inplace = True),
                nn.Linear(4096, num_classes))            
        elif name.startswith('vgg'):
            self.name = CP.MODULE_NAMES[1] # vgg
            self.features   = model.features
            self.classifier = nn.Sequential(
                nn.Linear(512*7*7, 4096), # 25088 -> 4096
                nn.ReLU(inplace = True),
                nn.Dropout(p = 0.5),
                nn.Linear(4096, 4096),
                nn.ReLU(inplace = True),
                nn.Dropout(p = 0.5),
                nn.Linear(4096, num_classes))            
        #elif self.name.startswith('resnet'):
        #   kinda more complicated to do than alex and vgg nets.
        #   will do later on.          
        else:
            raise NotImplementedError
            
        # freeze the feature extraction parameters.
        for params in self.features.parameters():
            params.requires_grad = False

    def forward(self, inp):
        inp = self.features(inp)
        inp = inp.view(inp.size(0), -1) # flatten the convolutional output to (batch_size x #neurons)
        inp = self.classifier(inp)
        return inp

    # def extract_features(self, inp):
    #     #features        = copy.deepcopy(self.features)
    #     classifier_list = list(copy.deepcopy(self.classifier))

    #     # how many of the last modules of the net should be popped to get to the second from the last modules output.
    #     num_pops = CP.FEATURE_POP_OPS[self.name]
    #     for _ in range(num_pops):
    #         classifier_list.pop()
        
    #     classifier = nn.Sequential(*classifier_list)
    #     # now run the 
    #     inp = self.features(inp)
    #     inp = inp.view(inp.size(0), -1) # flatten the convolutional output to (batch_size x #neurons)
    #     inp = classifier(inp)
    #     return inp

class ConvnetFeatures():
    def __init__(self, model):
        self.name       = model.name
        self.features   = copy.deepcopy(model.features)
        self.extractors = copy.deepcopy(model.classifier)
        self.num_pops   = CP.FEATURE_POP_OPS[model.name]
        self.__hook_fclayer__()

    def __hook_fclayer__(self):
        fclayer_list = list(self.extractors)
        for _ in range(self.num_pops):
            fclayer_list.pop()
        self.extractors = nn.Sequential(*fclayer_list)

    def __call__(self, inp):
        inp = self.features(inp)
        inp = np.view(inp.view(0), -1)
        inp = self.extractors(inp)
        return inp