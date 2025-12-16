#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VCF DUP记录修正工具

功能说明：
    本脚本用于处理VCF文件中包含DUP（重复序列）的记录，对符合条件的记录进行以下修正：
    1. 将REF列替换为POS位置在参考基因组中对应的碱基
    2. 将ALT列替换为<DUP>
    3. 将INFO列中的SVTYPE字段设置为DUP（如果原来为空或不存在，则添加；如果已存在，则更新）

使用方法：
    python 01.py -i input.vcf -o output.vcf -g genome.fasta [选项]

参数说明：
    -i, --input      输入VCF文件路径（必需）
    -o, --output     输出VCF文件路径（必需）
    -g, --genome     参考基因组FASTA文件路径（必需）
    -k, --keyword    用于匹配ID的关键词，默认为"DUP"
    -h, --help       显示帮助信息

示例：
    # 基本用法
    python 01.py -i merged.vcf -o output.vcf -g genome.fasta
    
    # 自定义关键词匹配
    python 01.py -i merged.vcf -o output.vcf -g genome.fasta -k DUP

依赖库：
    - vcfpy: VCF文件读写库
    - pyfaidx: FASTA文件快速访问库

安装依赖：
    pip install vcfpy pyfaidx

作者：zhangzhishuai
日期：2025-12-16
"""

import argparse
import sys
import vcfpy
from pyfaidx import Fasta


def process_vcf(input_vcf, output_vcf, genome_fasta, keyword="DUP"):
    """
    处理VCF文件，修正包含指定关键词的DUP记录
    
    参数:
        input_vcf (str): 输入VCF文件路径
        output_vcf (str): 输出VCF文件路径
        genome_fasta (str): 参考基因组FASTA文件路径
        keyword (str): 用于匹配ID的关键词，默认为"DUP"
    
    返回:
        int: 处理的记录数量
    """
    try:
        # 读取基因组文件
        print(f"正在读取参考基因组文件: {genome_fasta}")
        genome = Fasta(genome_fasta)
        
        # 读取VCF文件
        print(f"正在读取输入VCF文件: {input_vcf}")
        reader = vcfpy.Reader.from_path(input_vcf)
        
        # 创建输出VCF文件Writer
        print(f"正在创建输出VCF文件: {output_vcf}")
        writer = vcfpy.Writer.from_path(output_vcf, reader.header)
        
        processed_count = 0
        
        # 遍历VCF记录
        print("开始处理VCF记录...")
        for record in reader:
            # 检查ID列是否包含指定关键词（支持ID为列表或字符串）
            id_list = record.ID if isinstance(record.ID, list) else [record.ID]
            if record.ID and any(keyword in str(_id) for _id in id_list):
                try:
                    # 获取染色体名称
                    chrom = record.CHROM
                    
                    # 获取POS位置的碱基（VCF中POS是1-based，pyfaidx是0-based）
                    pos = record.POS
                    ref_base = genome[chrom][pos - 1:pos].seq.upper()
                    
                    # 替换REF为pos位置的碱基
                    record.REF = ref_base
                    
                    # 替换ALT为<DUP>
                    record.ALT = [vcfpy.SymbolicAllele("DUP")]
                    
                    # 修改INFO列中的SVTYPE
                    # 将SVTYPE设置为DUP（无论原来是否存在或为空）
                    record.INFO["SVTYPE"] = "DUP"
                    
                    processed_count += 1
                    
                except KeyError as e:
                    print(f"警告: 染色体 {chrom} 在参考基因组中不存在，跳过记录 POS={pos}", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"警告: 处理记录 CHROM={record.CHROM} POS={record.POS} 时出错: {e}", file=sys.stderr)
                    continue
            
            # 写入记录
            writer.write_record(record)
        
        # 关闭文件
        writer.close()
        reader.close()
        genome.close()
        
        print(f"处理完成！共处理了 {processed_count} 条包含'{keyword}'的记录。")
        return processed_count
        
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """主函数：解析命令行参数并执行处理"""
    parser = argparse.ArgumentParser(
        description="VCF DUP记录修正工具 - 修正VCF文件中包含DUP的记录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s -i input.vcf -o output.vcf -g genome.fasta
  %(prog)s -i input.vcf -o output.vcf -g genome.fasta -k DUP

功能说明:
  本脚本会处理VCF文件中ID列包含指定关键词（默认为"DUP"）的记录：
  - REF列：替换为POS位置在参考基因组中对应的碱基
  - ALT列：替换为<DUP>
  - INFO列：将SVTYPE字段设置为DUP
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入VCF文件路径（必需）"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="输出VCF文件路径（必需）"
    )
    
    parser.add_argument(
        "-g", "--genome",
        required=True,
        help="参考基因组FASTA文件路径（必需）"
    )
    
    parser.add_argument(
        "-k", "--keyword",
        default="DUP",
        help="用于匹配ID的关键词（默认: DUP）"
    )
    
    args = parser.parse_args()
    
    # 执行处理
    process_vcf(args.input, args.output, args.genome, args.keyword)


if __name__ == "__main__":
    main()


