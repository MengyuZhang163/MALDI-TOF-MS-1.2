# 📦 ZIP文件夹批量上传指南

## 为什么使用ZIP上传？

当你有**几十个甚至上百个TXT文件**时，逐个选择非常麻烦。ZIP压缩包上传可以：
- ✅ 一次性上传所有文件
- ✅ 保持文件夹结构
- ✅ 节省上传时间
- ✅ 避免遗漏文件

---

## 📋 快速开始（3步完成）

### 步骤1: 准备文件夹

将所有文件放入一个文件夹：

```
我的实验数据/
├── sample001.txt
├── sample002.txt
├── sample003.txt
├── ...
├── sample100.txt
└── sample_labels.xlsx
```

**重要提示:**
- ✅ TXT和Excel文件可以在同一文件夹
- ✅ 子文件夹中的TXT也会被识别
- ✅ Excel文件只需要1个
- ⚠️ 确保Excel中的`file`列与TXT文件名完全匹配

### 步骤2: 压缩为ZIP

**Windows系统:**
1. 右键点击文件夹
2. 选择"发送到" → "压缩(zipped)文件夹"
3. 重命名为 `train_data.zip`

**macOS系统:**
1. 右键点击文件夹
2. 选择"压缩 [文件夹名]"
3. 重命名为 `train_data.zip`

**Linux系统:**
```bash
zip -r train_data.zip 我的实验数据/
```

### 步骤3: 上传到应用

1. 启动应用: `streamlit run maldi_app_enhanced.py`
2. 选择"📦 方式1: ZIP压缩包上传"
3. 点击上传区域，选择你的ZIP文件
4. 等待自动解压和验证

---

## 📁 文件结构示例

### 示例1: 简单结构（推荐）

```
train_data.zip
├── sample1.txt
├── sample2.txt
├── sample3.txt
├── sample4.txt
└── labels.xlsx
```

### 示例2: 带子文件夹结构

```
experiment_batch1.zip
├── resistant_group/
│   ├── R001.txt
│   ├── R002.txt
│   └── R003.txt
├── sensitive_group/
│   ├── S001.txt
│   ├── S002.txt
│   └── S003.txt
└── sample_info.xlsx
```

**注意:** 应用会自动提取所有子文件夹中的TXT文件

### 示例3: 训练集 + 验证集

分别压缩两个ZIP：

**train_data.zip:**
```
├── train001.txt
├── train002.txt
├── ...
└── labels.xlsx
```

**validation_data.zip:**
```
├── valid001.txt
├── valid002.txt
└── ...
```

---

## ✅ Excel标签文件要求

### 必须包含的列

| 列名 | 说明 | 示例 |
|------|------|------|
| `file` | TXT文件名（含扩展名） | sample1.txt |
| `group` | 分组标签 | Resistant |

### Excel示例

| file | group |
|------|-------|
| sample001.txt | Resistant |
| sample002.txt | Resistant |
| sample003.txt | Sensitive |
| sample004.txt | Sensitive |

### 常见错误 ❌

1. **文件名不匹配**
   - Excel: `sample1.txt`
   - 实际文件: `Sample1.txt` (大小写不同)
   - ✅ 解决: 确保大小写完全一致

2. **缺少扩展名**
   - Excel: `sample1` ❌
   - 应该是: `sample1.txt` ✅

3. **列名错误**
   - 使用了 `filename` 而不是 `file` ❌
   - 使用了 `category` 而不是 `group` ❌

---

## 🔧 验证ZIP文件

### Windows验证方法
1. 双击ZIP文件预览
2. 确认能看到所有TXT和Excel文件
3. 检查文件数量是否正确

### macOS验证方法
```bash
# 查看ZIP内容
unzip -l train_data.zip

# 输出示例:
# Archive:  train_data.zip
#   Length      Date    Time    Name
# ---------  ---------- -----   ----
#     12345  01-30-2024 10:00   sample1.txt
#     12346  01-30-2024 10:00   sample2.txt
#      8901  01-30-2024 10:00   labels.xlsx
```

---

## 💡 最佳实践

### 1. 命名规范
- 使用简短、有意义的文件名
- 避免特殊字符: `@ # $ % & * ( ) [ ]`
- 推荐格式: `sample001.txt`, `sample002.txt`

### 2. 文件组织
```
项目根目录/
├── 训练集/
│   ├── 所有训练TXT文件
│   └── labels.xlsx
├── 验证集/
│   └── 所有验证TXT文件
└── README.txt (可选)
```

### 3. 批量重命名

如果文件名不规范，可以批量重命名：

**Windows (PowerShell):**
```powershell
# 批量添加前缀
Get-ChildItem *.txt | Rename-Item -NewName {$_.Directory.Name + "_" + $_.Name}
```

**macOS/Linux:**
```bash
# 批量添加编号
counter=1
for file in *.txt; do
    mv "$file" "sample$(printf %03d $counter).txt"
    ((counter++))
done
```

---

## ❓ 常见问题

### Q1: ZIP太大无法上传怎么办？
**方案1:** 分批压缩上传
```
train_batch1.zip (50个文件)
train_batch2.zip (50个文件)
train_batch3.zip (剩余文件)
```

**方案2:** 只压缩TXT文件，Excel单独上传
- 使用单个文件上传方式上传Excel
- 使用ZIP上传TXT文件

### Q2: 解压失败怎么办？
可能原因：
- ZIP文件损坏 → 重新压缩
- 文件名包含特殊字符 → 重命名后重新压缩
- 网络中断 → 重新上传

### Q3: 能上传RAR或7Z格式吗？
目前仅支持ZIP格式。请转换：
- WinRAR: 右键 → 添加到压缩文件 → 选择ZIP格式
- 7-Zip: 右键 → 7-Zip → 添加到压缩包 → 选择ZIP格式

### Q4: ZIP中有多个Excel文件怎么办？
应用会自动选择第一个Excel文件。建议：
- 只在ZIP中放一个Excel文件
- 或者将额外的Excel文件重命名为`.txt`后缀（如果是备份）

### Q5: 子文件夹结构会被保留吗？
不会。应用会提取所有TXT文件，忽略文件夹结构。最终只保留文件名。

---

## 🎯 完整示例工作流程

### 场景: 处理100个样本的实验数据

#### 1. 准备阶段
```bash
实验数据/
├── batch1/
│   ├── R001.txt ~ R025.txt (25个耐药样本)
│   └── S001.txt ~ S025.txt (25个敏感样本)
├── batch2/
│   ├── R026.txt ~ R050.txt
│   └── S026.txt ~ S050.txt
└── sample_labels.xlsx
```

#### 2. 创建Excel
在 `sample_labels.xlsx` 中：

| file | group |
|------|-------|
| R001.txt | Resistant |
| R002.txt | Resistant |
| ... | ... |
| S001.txt | Sensitive |
| ... | ... |

#### 3. 压缩
```bash
# 压缩整个文件夹
zip -r experiment_data.zip 实验数据/
```

#### 4. 上传
1. 启动应用
2. 选择ZIP上传方式
3. 上传 `experiment_data.zip`
4. 查看解压结果: "✅ 成功解压：100个TXT文件 + 1个Excel文件"

#### 5. 处理
1. 检查Excel预览确认格式正确
2. 选择自动参数估计（或手动调整）
3. 点击"开始处理"
4. 下载结果

---

## 📊 性能提示

### ZIP文件大小建议

| 文件数量 | 单文件大小 | ZIP大小估计 | 上传时间 |
|---------|-----------|------------|---------|
| 10个 | ~50KB | ~500KB | <5秒 |
| 50个 | ~50KB | ~2.5MB | ~10秒 |
| 100个 | ~50KB | ~5MB | ~20秒 |
| 500个 | ~50KB | ~25MB | ~1分钟 |

**如果ZIP超过50MB:**
- 建议分批上传
- 或者使用应用的批量处理模式

---

## 🛠️ 故障排除

### 问题: 上传后看不到文件
**检查清单:**
- [ ] ZIP是否正确解压（尝试在电脑上解压测试）
- [ ] 文件扩展名是否为`.txt`（区分大小写）
- [ ] ZIP是否包含`__MACOSX`等系统文件夹（应用会自动忽略）

### 问题: Excel验证失败
**检查清单:**
- [ ] 列名是否准确为`file`和`group`（区分大小写）
- [ ] 文件名是否包含扩展名（如`.txt`）
- [ ] Excel格式是否为`.xlsx`或`.xls`

### 问题: 处理时间过长
**可能原因:**
- 文件过多（>200个）
- TXT文件过大（单个>1MB）
- 网络不稳定

**解决方案:**
- 分批处理
- 检查TXT文件格式（是否有异常大的文件）
- 使用本地Python脚本处理（不经过网页）

---

## 📞 获取帮助

如果遇到问题：
1. 检查本指南的常见问题部分
2. 验证ZIP文件内容
3. 尝试使用演示数据测试应用
4. 查看应用的错误提示信息

---

**祝您使用顺利！** 🎉
