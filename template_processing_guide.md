# 基于训练集的稳定特征模版处理方案

## 📋 核心理念

**策略**: 先用训练集建立稳定的特征框架（模版），然后所有后续验证集都使用这个模版提取强度。

**优势**:
1. ✅ 所有数据集特征完全一致
2. ✅ 训练集确定特征，验证集无需重新检峰
3. ✅ 可处理无限多批次验证集
4. ✅ 保证模型的可复现性和稳定性

---

## 🔄 处理流程对比

### ❌ 原始方法（问题）
```
训练集 → 检峰 → 特征A (285个)
验证集 → 检峰 → 特征B (不同)
结果: 特征不一致，无法建模
```

### ⚠️ 网站方法（不适合多批次）
```
训练集 + 验证集 → 合并检峰 → 特征C (100个)
问题: 每次新验证集都需要重新处理训练集
```

### ✅ 模版方法（推荐）
```
阶段1: 训练集 → 检峰 → 建立特征模版
阶段2: 验证集1 → 使用模版提取强度
阶段3: 验证集2 → 使用模版提取强度
阶段4: 验证集N → 使用模版提取强度
结果: 所有数据集特征完全一致
```

---

## 📊 处理流程详解

### 阶段1: 建立训练集特征模版

```r
# 1. 读取和预处理训练集
training_spectra <- importTxt(train_path)
training_spectra <- transformIntensity(training_spectra, method = "sqrt")
training_spectra <- smoothIntensity(..., halfWindowSize = 90)
training_spectra <- removeBaseline(..., iterations = 100)
training_spectra <- calibrateIntensity(..., method = "TIC")

# 2. 计算平均谱
avgSpectra <- averageMassSpectra(training_spectra, labels = train_labels)

# 3. 对齐
avgSpectra <- alignSpectra(avgSpectra, ...)

# 4. 只在训练集上检测峰（关键！）
train_peaks <- detectPeaks(avgSpectra, ...)
train_binned <- binPeaks(train_peaks, tolerance = 2)

# 5. 提取特征m/z（这是模版！）
feature_mz <- unique(unlist(lapply(train_binned, function(p) p@mass)))
feature_mz <- sort(feature_mz)

# 6. 保存特征模版
write.csv(data.frame(mz = feature_mz), 'feature_template.csv')
```

**输出:**
- `peak_intensity_train.csv` - 训练集强度矩阵
- `feature_template.csv` - 特征模版（关键！）

---

### 阶段2: 使用模版处理验证集

```r
# 1. 读取和预处理验证集（使用训练集相同参数）
validation_spectra <- importTxt(valid_path)
validation_spectra <- transformIntensity(..., method = "sqrt")
validation_spectra <- smoothIntensity(..., halfWindowSize = 90)  # 同训练集
validation_spectra <- removeBaseline(..., iterations = 100)      # 同训练集
validation_spectra <- calibrateIntensity(..., method = "TIC")

# 2. 对齐（使用训练集参数）
validation_spectra <- alignSpectra(..., halfWindowSize = 90, SNR = 2)

# 3. 不需要检峰！直接使用模版提取强度
for each sample in validation_spectra:
    for each feature_mz in template:
        intensity = extract_intensity_at(feature_mz, tolerance = 2)

# 4. 生成强度矩阵（列与训练集完全一致）
```

**输出:**
- `peak_intensity_validation.csv` - 验证集强度矩阵（特征与训练集一致）

---

## 🔑 关键技术细节

### 1. 特征模版的定义

特征模版就是训练集检测到的峰的m/z位置列表：

```r
# 示例特征模版
feature_mz:
  [2012, 2031, 2051, 2074, 2090, ..., 15415, 16486, 19081]
```

这个列表定义了:
- 有哪些特征（m/z位置）
- 特征的顺序
- 最终矩阵的列

---

### 2. 从验证集提取强度的方法

```r
# 对于验证集的每个样本
for (i in 1:n_samples) {
  spec <- validation_spectra[[i]]
  
  # 对于模版中的每个特征
  for (j in 1:n_features) {
    target_mz <- template_mz[j]
    
    # 在该样本的光谱中找到最接近target_mz的强度
    # 使用与训练集binning相同的容差（±2 Da）
    idx <- which(abs(spec@mass - target_mz) <= 2)
    
    if (length(idx) > 0) {
      # 取最接近的那个
      closest_idx <- idx[which.min(abs(spec@mass[idx] - target_mz))]
      intensity_matrix[i, j] <- spec@intensity[closest_idx]
    } else {
      # 如果该样本在此m/z没有峰，强度为0
      intensity_matrix[i, j] <- 0
    }
  }
}
```

**关键点:**
- 不在验证集上检峰
- 直接在预设的m/z位置提取强度
- 使用插值或最近邻方法

---

### 3. 参数一致性保证

**必须保持一致的参数:**

| 参数 | 训练集 | 验证集 | 说明 |
|------|-------|-------|------|
| transformIntensity | sqrt | sqrt | 强度转换 |
| halfWindowSize | 90 | 90 | 平滑和对齐 |
| iterations | 100 | 100 | 基线去除 |
| calibrateIntensity | TIC | TIC | 归一化方法 |
| SNR | 2 | 2 | 信噪比 |
| tolerance | 0.008 | 0.008 | 对齐容差 |
| binning tolerance | 2 | 2 | 提取强度容差 |

**建议**: 将这些参数保存为配置文件

```r
processing_params <- list(
  halfWindowSize = 90,
  SNR = 2,
  tolerance = 0.008,
  iterations = 100,
  binning_tolerance = 2
)

saveRDS(processing_params, 'processing_params.rds')
```

---

## 📁 文件结构

```
项目目录/
├── 训练集/
│   ├── 1.txt, 2.txt, ..., 1219.txt
│   ├── wurulian.xlsx
│   ├── peak_intensity_train.csv         # 输出
│   ├── feature_template.csv              # 输出（关键！）
│   └── processing_params.rds             # 输出
│
├── 验证集1/
│   ├── valid1.txt, valid2.txt, ...
│   └── peak_intensity_validation.csv     # 输出
│
├── 验证集2/
│   ├── batch2_1.txt, batch2_2.txt, ...
│   └── peak_intensity_validation_batch2.csv  # 输出
│
└── template_based_processing.R           # 处理脚本
```

---

## 🚀 使用步骤

### 步骤1: 处理训练集，建立模版

```r
# 运行脚本的第一部分
source('template_based_processing.R')

# 或者单独运行
Rscript template_based_processing.R
```

**检查输出:**
- [ ] `peak_intensity_train.csv` 已生成
- [ ] `feature_template.csv` 已生成
- [ ] 查看特征数量和m/z范围

---

### 步骤2: 处理第一批验证集

```r
# 修改验证集路径
valid_path_1 <- "你的验证集路径"

# 运行处理函数
validation_df_1 <- process_validation_set(valid_path_1, feature_mz, processing_params)

# 保存
write.csv(validation_df_1, 'peak_intensity_validation.csv', row.names = FALSE)
```

---

### 步骤3: 处理后续验证集

```r
# 第二批
validation_df_2 <- process_validation_set(valid_path_2, feature_mz, processing_params)
write.csv(validation_df_2, 'validation_batch2.csv', row.names = FALSE)

# 第三批
validation_df_3 <- process_validation_set(valid_path_3, feature_mz, processing_params)
write.csv(validation_df_3, 'validation_batch3.csv', row.names = FALSE)

# ... 无限多批
```

---

## ✅ 验证特征一致性

```r
# 读取数据
train <- read.csv('peak_intensity_train.csv')
valid1 <- read.csv('peak_intensity_validation.csv')
valid2 <- read.csv('peak_intensity_validation_batch2.csv')

# 检查列名
train_features <- colnames(train)[-1]  # 去掉第一列（样本名）
valid1_features <- colnames(valid1)[-1]
valid2_features <- colnames(valid2)[-1]

# 验证
all(train_features == valid1_features)  # 应该返回TRUE
all(train_features == valid2_features)  # 应该返回TRUE

# 查看特征数
length(train_features)  # 例如: 285
```

---

## 📊 预期结果

### 训练集
```csv
group,mz_2012,mz_2031,mz_2051,...,mz_19081
F1,0.000234,0.001234,0.000543,...,0.000012
F2,0.000123,0.002345,0.000234,...,0.000023
...
T1219,0.000456,0.001456,0.000678,...,0.000034
```

### 验证集1
```csv
sample,mz_2012,mz_2031,mz_2051,...,mz_19081
valid1.txt,0.000345,0.001567,0.000789,...,0.000045
valid2.txt,0.000234,0.002678,0.000456,...,0.000056
...
```

### 验证集2
```csv
sample,mz_2012,mz_2031,mz_2051,...,mz_19081
batch2_1.txt,0.000567,0.001789,0.000890,...,0.000067
batch2_2.txt,0.000678,0.002890,0.000567,...,0.000078
...
```

**关键**: 所有文件的列（特征）完全相同！

---

## ⚠️ 关于强度异常的问题

### 问题: 为什么我的强度值这么小？

你的原始代码生成的强度在 10^-7 到 10^-5 范围，这可能是因为:

1. **TIC归一化的影响**
   ```r
   calibrateIntensity(training_spectra, method = "TIC")
   ```
   - TIC会将每个谱的总强度归一化为1
   - 如果有很多峰，每个峰的强度就会很小

2. **averageMassSpectra的问题**
   - 在某些MALDIquant版本中可能有bug
   - 平均后强度可能异常缩放

### 解决方案1: 检查MALDIquant版本

```r
# 检查版本
packageVersion("MALDIquant")

# 更新到最新版
install.packages("MALDIquant")

# 推荐版本: >= 1.19.3
```

---

### 解决方案2: 调整归一化方法

```r
# 尝试不同的归一化方法

# 选项1: 使用最大值归一化
training_spectra <- calibrateIntensity(training_spectra, method = "PQN")

# 选项2: 不归一化
# 注释掉这行
# training_spectra <- calibrateIntensity(training_spectra, method = "TIC")

# 选项3: 自定义归一化
for (i in seq_along(training_spectra)) {
  max_int <- max(training_spectra[[i]]@intensity)
  training_spectra[[i]]@intensity <- training_spectra[[i]]@intensity / max_int * 1000
}
```

---

### 解决方案3: 后处理缩放

```r
# 在生成强度矩阵后，统一缩放到合理范围

# 读取强度矩阵
intensity_matrix <- intensityMatrix(train_binned, avgSpectra)

# 缩放到0-1000范围
max_val <- max(intensity_matrix)
min_val <- min(intensity_matrix)
intensity_matrix_scaled <- (intensity_matrix - min_val) / (max_val - min_val) * 1000

# 或者简单乘以一个因子
intensity_matrix_scaled <- intensity_matrix * 100000
```

---

## 🔧 故障排除

### 问题1: 特征数量过多（285个）

**原因**: SNR阈值太低，检测到太多噪声峰

**解决**:
```r
# 提高SNR阈值
train_peaks <- detectPeaks(avgSpectra,
                           method = "MAD",
                           halfWindowSize = 90,
                           SNR = 5)  # 从2改为5
```

---

### 问题2: m/z范围太宽（2012-19081）

**原因**: 高m/z区域可能是噪声或二聚体

**解决**:
```r
# 过滤特征m/z范围
feature_mz <- feature_mz[feature_mz >= 1000 & feature_mz <= 12000]
```

---

### 问题3: 验证集某些样本强度全为0

**原因**: 验证集数据质量差，或对齐失败

**解决**:
```r
# 检查对齐质量
plot(validation_spectra[[1]])

# 尝试更宽松的提取容差
# 从 tolerance = 2 改为 tolerance = 5
idx <- which(abs(spec@mass - target_mz) <= 5)
```

---

## 📊 与网站方法的对比

| 特性 | 模版方法 | 网站方法 |
|------|---------|---------|
| **特征一致性** | ✅ 完美 | ✅ 完美 |
| **多批次处理** | ✅ 优秀 | ⚠️ 每次需重新处理训练集 |
| **强度数值** | ⚠️ 需调整 | ✅ 正常 |
| **处理速度** | ✅ 快 | ⚠️ 慢（需重新处理全部） |
| **灵活性** | ✅ 高 | ⚠️ 低 |
| **可复现性** | ✅ 完美 | ✅ 好 |

---

## 💡 最佳实践建议

### 1. 保存处理参数
```r
processing_params <- list(
  halfWindowSize = 90,
  SNR = 2,
  tolerance = 0.008,
  iterations = 100,
  date = Sys.Date(),
  maldi_version = packageVersion("MALDIquant")
)
saveRDS(processing_params, 'processing_params.rds')
```

### 2. 记录特征模版信息
```r
template_info <- data.frame(
  feature_id = paste0("mz_", round(feature_mz)),
  mz = feature_mz,
  mz_min = feature_mz - 2,  # binning范围
  mz_max = feature_mz + 2
)
write.csv(template_info, 'feature_template_detailed.csv', row.names = FALSE)
```

### 3. 质量控制检查
```r
# 检查训练集强度分布
summary(as.vector(train_intensity_matrix))

# 检查验证集强度分布
summary(as.vector(validation_intensity_matrix))

# 检查零值比例
zero_ratio <- sum(validation_intensity_matrix == 0) / length(validation_intensity_matrix)
cat(sprintf("零值比例: %.2f%%\n", zero_ratio * 100))
```

---

## 🎯 总结

**核心优势**:
1. ✅ 训练集定义特征，所有验证集使用相同特征
2. ✅ 可处理无限多批次验证集
3. ✅ 保证特征完全一致
4. ✅ 处理速度快（验证集无需检峰）
5. ✅ 模型稳定可复现

**使用场景**:
- ✅ 有多批次验证集需要处理
- ✅ 需要建立稳定的预测模型
- ✅ 需要保证特征一致性
- ✅ 追求高可复现性

**注意事项**:
- ⚠️ 需要解决强度数值异常问题
- ⚠️ 确保所有批次使用相同处理参数
- ⚠️ 定期检查数据质量

---

**这个方案完美符合你的需求：建立稳定的训练集模版，然后批量处理多批验证集！**
