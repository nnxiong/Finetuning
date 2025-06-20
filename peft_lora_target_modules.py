'''
在使用 PEFT（Parameter-Efficient Fine-Tuning）时，通常需要指定哪些模块需要进行适配。以下是一些常见的模块匹配规则：
# 1. 指定 target_modules 
- /home/zhongrongmiao/anaconda3/envs/ProteinMPNN/lib/python3.8/site-packages/peft/utils/constants.py 中没有该模型对应的target_modules
# 2. 不指定 target_modules
- /home/zhongrongmiao/anaconda3/envs/ProteinMPNN/lib/python3.8/site-packages/peft/utils/constants.py 中有该模型对应的target_modules

部分模块匹配规则​​：
​​注意力层​​：自动识别 q_proj、k_proj、v_proj、o_proj（LLaMA 风格）或 query、key、value、dense（BERT 风格）等。
​​前馈网络（FFN）​​：适配 gate_proj、up_proj、down_proj（SwiGLU 结构）或 intermediate.dense、output.dense（传统 MLP）。


在图像分类任务中，分类模型实际上由 backbone 和 classifier 组成，前者用于特征提取，后者用于分类。
AutoModel 和 AutoModelForXXX 之间也存在类似的关系，可以理解为 AutoModel 对应于 backbone，
而 AutoModelForXXX 则是 backbone + classifier，也就是完整的模型。

1. AutoModel.from_pretrained​​
​​功能​​
​​通用模型加载​​：返回模型的​​基础架构​​（如 Transformer 的编码器或解码器），​​不包含任务特定的头部​​（如语言模型头、分类头等）。
​​适用场景​​：
需要自定义任务头（如自己添加分类层或回归层）。
仅需模型的中间层表示（如特征提取）。
多模态或特殊架构的灵活扩展。

2. AutoModelForCausalLM.from_pretrained​​
​​功能​​
​​任务专用加载​​：返回​​完整的因果语言模型​​，包含基础架构和预训练的任务头（如语言模型头 lm_head）。
​​适用场景​​：
直接用于文本生成（如 GPT、LLaMA）。
微调因果语言模型（如续写、对话生成）。


可参考链接：https://blog.csdn.net/weixin_42426841/article/details/142236561


方法	返回值	是否包含参数名	典型用途
model.parameters()	生成器（parameter）	❌ 否	通用优化器输入（如 optimizer = torch.optim.SGD(model.parameters())）
model.named_parameters()	生成器（(name, parameter)）	✅ 是	需要参数名的操作（如选择性冻结、初始化、调试）

ep:
import torch
import torch.nn as nn

# 定义一个简单模型
model = nn.Sequential(
    nn.Linear(10, 20),  # 参数: weight (20x10), bias (20)
    nn.ReLU(),
    nn.Linear(20, 1)    # 参数: weight (1x20), bias (1)
)

# 遍历所有参数（无名称）
for param in model.parameters():
    print(f"Shape: {param.shape}, Requires_grad: {param.requires_grad}")

Shape: torch.Size([20, 10]), Requires_grad: True
Shape: torch.Size([20]), Requires_grad: True
Shape: torch.Size([1, 20]), Requires_grad: True
Shape: torch.Size([1]), Requires_grad: True

'''

from peft import LoraConfig, get_peft_model
from transformers import (AutoModel, AutoModelForCausalLM, AutoTokenizer)

# ​​即使加载本地模型​​，如果该模型包含自定义代码（如非 transformers 官方支持的架构或分词器），仍然需要设置 trust_remote_code=True
model = AutoModelForCausalLM.from_pretrained('/mnt/data2/model/Qwen/Qwen2-7B-Instruct', trust_remote_code=True)
# model = AutoModel.from_pretrained('/mnt/data2/model/Qwen/Qwen2-7B-Instruct', trust_remote_code=True)
# 查看模型的参数 找到 self attention 模块 和 FNN前馈网络模块
for name,param in model.named_parameters():
    print(name)

# 指定 target_modules
config = LoraConfig(
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    task_type="CAUSAL_LM")  # 不指定 target_modules
peft_model = get_peft_model(model, config)
# 查看实际适配的模块
print(config.target_modules)

# ​​PEFT 库会成功匹配并适配所有指定的目标模块​​， 从 model.layers.0 —— model.layers.n-1 中的每一层都将应用 LoRA 适配器。

# model = AutoModelForCausalLM.from_pretrained('/mnt/data1/zhongrongmiao/InternLM/internlm2_5-1_8b-chat', trust_remote_code=True)
model = AutoModel.from_pretrained('/mnt/data1/zhongrongmiao/InternLM/internlm2_5-1_8b-chat', trust_remote_code=True)
# 查看模型的参数 找到 attention 模块 和 FNN前馈网络模块
for name,param in model.named_parameters():
    print(name)
# 指定 target_modules
config = LoraConfig(
    target_modules=["wqkv", "wo", "w1", "w2", "w3"],
    task_type="CAUSAL_LM")  # 不指定 target_modules
peft_model = get_peft_model(model, config)
# 查看实际适配的模块
print(config.target_modules)
