# Reading mode 与原始实现核对

固定官方版本：`19c6dc90e7a0dddb1a241b73e7fae708b68f024e`（2024-10-25）。

- [main_reed_wm.py](https://github.com/facebookresearch/radioactive-watermark/blob/19c6dc90e7a0dddb1a241b73e7fae708b68f024e/main_reed_wm.py)
- [wm/detector.py](https://github.com/facebookresearch/radioactive-watermark/blob/19c6dc90e7a0dddb1a241b73e7fae708b68f024e/wm/detector.py)
- [论文 §4](https://arxiv.org/html/2402.14904v2#S4)

## 默认 official 模式

| 步骤 | 官方代码 | 本实现 |
|---|---|---|
| 顺序 | Random(fake_seed=0).shuffle(lines) | 同一 Python 算法及 seed，源 Parquet 行等价于 lines |
| 编码 | tokenize 后 convert_tokens_to_ids | 相同 API，不加特殊 token，并核验与 encode(False) 相同 |
| 布局 | 无分隔拼接；完整256-token块；丢弃尾部 | 相同，另记录来源ID和流偏移 |
| 前向 | 固定输入、eval、inference_mode，FP16 | 相同；batch默认1而非16，显式mask/use_cache=False |
| 预测 | topk=1，完整模型输出logits | torch.topk(k=1)，保留dtype及并列行为；词表外预测报错 |
| k=1索引 | target=x[1:]；target[j]配outputs[j+1] | x[1:L-1]配predictions[1:]，L−2候选 |
| attention tape | 当前块已遇窗口排除，首窗口x[1] | 相同；包含被pair tape排除的窗口，不含x[0] |
| corpus pair tape | 全局dic[(窗口,模型预测)]只计首次 | 相同，全检测语料共享集合 |
| Maryland p | betainc(G,1+N-G,gamma) | binom.sf(G−1,N,q)，G≥1时等价 |

论文文字概括为排除attention span中已出现窗口；官方代码实际从target=x[1:]维护tape。
official模式保留该索引，documents模式单独用于回答边界敏感性分析。

## 必须披露的适配及补充评估

1. **生成端水印**：本项目为CUDA simple_1、k=1、gamma=.5、key=15485863。作者hash/CPU PRNG及示例k=2/4、gamma=.25并非本项目生成协议。通过wm_data.kgw共用真实绿表；不能换成另一绿表后声称检测同一水印。
2. **语料**：500条教师held-out水印回答，与作者模型/数据不同。核验教师/学生tokenizer兼容和教师训练ID不重叠，不声称完成近重复或全部变换训练语料审计。
3. **完整处理**：不复制作者脚本batch截断/循环上界问题，处理全部完整块，报告块数、读取token、候选位置及有效N。
4. **数值边界**：N=0不检验，G=0时p=1；原beta函数G=0未定义。保留低于作者eps=1e-200的log尾概率，不截断排序。展示核对可另裁p下限至1e-200，裁剪并列不是实际排序。
5. **预算ROC**：1k/2k/3k候选位置分组、组内pair去重、AUROC/TPR、p均值/中位数是补充指标。论文主要报告模型级累计log10(p)。明确区分读取量、候选数与N。
6. **WN**：intrinsic与同一checkpoint的kgw_gad一致。WN调整后top-1是行为扩展，采用原规则/强度、FP32逆向bias、匹配clean对照，不能称为作者原始方法或权重净化证据。
7. **追溯**：源文本、模型、规则、tokenizer、环境及参数写入输出。禁止混用不同教师输入块。资产身份含配置哈希及权重大小/mtime，未全量哈希权重。

## 验证范围

test_reading.py独立转写原target/outputs循环，逐项核对k=1计分；G≥1时比较scipy.special.betainc与二项尾概率；另覆盖shuffle、拼接、尾部、topk并列、WN原处理器及完整CPU缓存汇总入口。

本地没有真实权重和CUDA，不能声称通过官方模型输出逐值比对。正式结果须在服务器跑实际checkpoint，并结合base、clean_warmup、clean_gad的误报检查解释。
