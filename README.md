# VCF DUP 记录修正工具

用于批量修正 VCF 文件中 ID 含指定关键词（默认 `DUP`）的记录，核心操作包括：
- 将 `REF` 替换为参考基因组对应 `POS` 位置的碱基
- 将 `ALT` 设置为 `<DUP>`（符号型等位基因）
- 将 `INFO` 中的 `SVTYPE` 设为 `DUP`

## 适用场景
- 针对结构变异（如 DUP）输出的 VCF，需要标准化 REF/ALT 与 INFO.SVTYPE
- 只处理 ID 中包含给定关键词的记录，其他记录保持原样写出

## 环境依赖
- Python 3.x（需避免使用系统自带的 Python 2）
- 依赖库：`vcfpy`、`pyfaidx`

安装依赖：
```bash
pip install vcfpy pyfaidx
```

## 输入/输出
- 输入：标准 VCF（支持压缩/索引以外的普通文本 VCF）
- 输出：处理后的 VCF（原 header 保留；被匹配的记录被修改后写出）

## 使用方法
```bash
python3 01.py -i input.vcf -o output.vcf -g genome.fasta [-k KEYWORD]
```

### 参数说明
- `-i, --input`   输入 VCF 文件路径（必需）
- `-o, --output`  输出 VCF 文件路径（必需）
- `-g, --genome`  参考基因组 FASTA 文件路径（必需，需要与 VCF 染色体命名匹配）
- `-k, --keyword` 匹配 ID 的关键词，默认 `DUP`
- `-h, --help`    显示帮助

### 示例
基本用法：
```bash
python3 01.py -i merged.vcf -o output.vcf -g /path/to/genome.fasta
```

自定义关键词：
```bash
python3 01.py -i merged.vcf -o output.vcf -g /path/to/genome.fasta -k DUP
```

## 工作流程概述
1) 读取参考基因组（pyfaidx，0-based）  
2) 读取输入 VCF（vcfpy）并复制 header  
3) 遍历记录：若 ID（字符串或列表）任一元素包含 `keyword`：  
   - `REF` <- 基因组 `CHROM:POS` 的碱基（POS 为 1-based）  
   - `ALT` <- `<DUP>`（`vcfpy.SymbolicAllele("DUP")`）  
   - `INFO["SVTYPE"]` <- `DUP`  
4) 逐条写入输出 VCF  

## 注意事项
- 请使用 `python3` 运行；`python` 可能指向 Python 2。  
- 确认参考基因组染色体命名与 VCF 一致，否则会提示缺失并跳过该记录。  
- 若输入 VCF 极大，可考虑压缩并索引，但当前脚本面向普通文本 VCF。  
- ALT 设置为符号型等位基因 `<DUP>`；若后续工具有特殊要求，请按需调整。  

## 开发者速览
- 核心脚本：`01.py`  
- 核心函数：`process_vcf(input_vcf, output_vcf, genome_fasta, keyword="DUP")`  
- 错误处理：缺失文件、缺失染色体会给出提示并退出或跳过记录。  

## 许可
内部使用示例脚本，如需发布请补充许可证声明。  

# repair-sv-vcf-file-from-jasmine
