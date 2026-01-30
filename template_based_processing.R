# ================================================================================
# MALDI-TOF MS 数据处理模版
# 策略: 以训练集为基准，建立稳定的特征框架，然后处理验证集
# ================================================================================

library('MALDIquant')
library('MALDIquantForeign')
library('readxl')

# ================================================================================
# 第一部分: 处理训练集，建立特征模版
# ================================================================================

cat("=" * 80, "\n")
cat("第一阶段: 处理训练集，建立特征框架\n")
cat("=" * 80, "\n")

# 1. 设置路径
train_path <- 'E:/RS/sm/耐药性分析/B/XUN/'
train_excel <- 'E:/RS/sm/耐药性分析/B/XUN/XUN-B.xlsx'

# 2. 读取训练集
setwd(train_path)
samples <- read_excel(train_excel)
training_spectra <- importTxt(getwd())
cat(sprintf("导入训练集: %d 个光谱\n", length(training_spectra)))

# 3. 训练集预处理（使用固定参数，确保可重复）
cat("\n执行预处理...\n")
training_spectra <- transformIntensity(training_spectra, method = "sqrt")
training_spectra <- smoothIntensity(training_spectra, method = "SavitzkyGolay", 
                                     halfWindowSize = 90)
training_spectra <- removeBaseline(training_spectra, method = "SNIP", 
                                   iterations = 100)
training_spectra <- calibrateIntensity(training_spectra, method = "TIC")

# 4. 分配标签
train_labels <- samples$group[match(
  sapply(training_spectra, function(s) basename(s@metaData$file)),
  samples$file
)]

# 5. 计算平均谱
avgSpectra <- averageMassSpectra(training_spectra, labels = train_labels)
cat(sprintf("计算平均谱: %d 个分组\n", length(avgSpectra)))

# 6. 对齐平均谱
avgSpectra <- alignSpectra(avgSpectra,
                           halfWindowSize = 90,
                           SNR = 2,
                           tolerance = 0.008,
                           warpingMethod = "lowess")

# ================================================================================
# 关键步骤: 只在训练集平均谱上检测峰，建立特征模版
# ================================================================================

cat("\n在训练集上检测峰，建立特征框架...\n")

# 7. 检测峰（只在训练集平均谱上）
train_peaks <- detectPeaks(avgSpectra,
                           method = "MAD",
                           halfWindowSize = 90,
                           SNR = 2)

# 8. 对检测到的峰进行binning
train_binned <- binPeaks(train_peaks, tolerance = 2)

# 9. 提取特征峰的m/z位置（这是模版的核心！）
feature_mz <- as.numeric(unique(unlist(lapply(train_binned, function(p) p@mass))))
feature_mz <- sort(feature_mz)

cat(sprintf("训练集特征数: %d 个峰\n", length(feature_mz)))
cat(sprintf("m/z范围: %.0f - %.0f\n", min(feature_mz), max(feature_mz)))

# 10. 保存特征模版（非常重要！）
feature_template <- data.frame(
  feature_id = paste0("mz_", round(feature_mz)),
  mz = feature_mz
)
write.csv(feature_template, 
          file = file.path(train_path, 'feature_template.csv'),
          row.names = FALSE)
cat("\n特征模版已保存: feature_template.csv\n")

# 11. 生成训练集强度矩阵
cat("\n生成训练集强度矩阵...\n")
train_intensity_matrix <- intensityMatrix(train_binned, avgSpectra)

# 处理列名和行名
bin_centers <- as.numeric(colnames(train_intensity_matrix))
bin_centers_integer <- round(bin_centers)
colnames(train_intensity_matrix) <- paste0("mz_", bin_centers_integer)
rownames(train_intensity_matrix) <- unique(train_labels)

# 保存训练集结果
train_df <- as.data.frame(train_intensity_matrix)
train_df <- cbind(group = rownames(train_df), train_df)
write.csv(train_df, 
          file = file.path(train_path, 'peak_intensity_train.csv'),
          row.names = FALSE)

cat(sprintf("\n训练集处理完成!\n"))
cat(sprintf("  分组数: %d\n", nrow(train_df)))
cat(sprintf("  特征数: %d\n", ncol(train_df) - 1))

# ================================================================================
# 第二部分: 基于训练集模版处理验证集
# ================================================================================

cat("\n" * 80, "\n")
cat("第二阶段: 基于训练集模版处理验证集\n")
cat("=" * 80, "\n")

# 定义处理验证集的函数
process_validation_set <- function(valid_path, template_mz, processing_params) {
  
  cat(sprintf("\n处理验证集: %s\n", valid_path))
  
  # 1. 导入验证集
  validation_spectra <- importTxt(valid_path)
  cat(sprintf("导入验证集: %d 个光谱\n", length(validation_spectra)))
  
  # 2. 使用与训练集完全相同的预处理参数
  cat("执行预处理（使用训练集相同参数）...\n")
  validation_spectra <- transformIntensity(validation_spectra, method = "sqrt")
  validation_spectra <- smoothIntensity(validation_spectra, 
                                        method = "SavitzkyGolay",
                                        halfWindowSize = processing_params$halfWindowSize)
  validation_spectra <- removeBaseline(validation_spectra, 
                                       method = "SNIP",
                                       iterations = processing_params$iterations)
  validation_spectra <- calibrateIntensity(validation_spectra, method = "TIC")
  
  # 3. 对齐（使用训练集参数）
  validation_spectra <- alignSpectra(validation_spectra,
                                     halfWindowSize = processing_params$halfWindowSize,
                                     SNR = processing_params$SNR,
                                     tolerance = processing_params$tolerance,
                                     warpingMethod = "lowess")
  
  # 4. 检测峰
  valid_peaks <- detectPeaks(validation_spectra,
                             method = "MAD",
                             halfWindowSize = processing_params$halfWindowSize,
                             SNR = processing_params$SNR)
  
  # ============================================================================
  # 关键步骤: 使用训练集的特征模版提取强度
  # ============================================================================
  
  cat("使用训练集特征模版提取强度...\n")
  
  # 创建强度矩阵，行=样本，列=训练集定义的特征
  n_samples <- length(validation_spectra)
  n_features <- length(template_mz)
  intensity_matrix <- matrix(0, nrow = n_samples, ncol = n_features)
  
  # 对每个验证集样本
  for (i in 1:n_samples) {
    spec <- validation_spectra[[i]]
    peaks <- valid_peaks[[i]]
    
    # 对每个模版特征
    for (j in 1:n_features) {
      target_mz <- template_mz[j]
      
      # 在该样本的谱中找到最接近target_mz的强度
      # 使用2 Da容差（与训练集binning一致）
      if (length(spec@mass) > 0) {
        idx <- which(abs(spec@mass - target_mz) <= 2)
        if (length(idx) > 0) {
          # 如果有多个匹配，取最接近的
          closest_idx <- idx[which.min(abs(spec@mass[idx] - target_mz))]
          intensity_matrix[i, j] <- spec@intensity[closest_idx]
        }
      }
    }
  }
  
  # 5. 设置列名和行名
  colnames(intensity_matrix) <- paste0("mz_", round(template_mz))
  
  sample_names <- sapply(validation_spectra, function(s) basename(s@metaData$file))
  rownames(intensity_matrix) <- sample_names
  
  # 6. 转换为数据框
  valid_df <- as.data.frame(intensity_matrix)
  valid_df <- cbind(sample = rownames(valid_df), valid_df)
  
  cat(sprintf("\n验证集处理完成!\n"))
  cat(sprintf("  样本数: %d\n", nrow(valid_df)))
  cat(sprintf("  特征数: %d (与训练集一致)\n", ncol(valid_df) - 1))
  
  return(valid_df)
}

# ================================================================================
# 处理第一批验证集
# ================================================================================

valid_path_1 <- "E:/RS/sm/耐药性分析/B/YAN/"

# 定义处理参数（与训练集一致）
processing_params <- list(
  halfWindowSize = 90,
  SNR = 2,
  tolerance = 0.008,
  iterations = 100
)

# 处理验证集
validation_df_1 <- process_validation_set(valid_path_1, feature_mz, processing_params)

# 保存验证集结果
write.csv(validation_df_1,
          file = file.path(valid_path_1, 'peak_intensity_validation.csv'),
          row.names = FALSE)

cat("\n第一批验证集已保存!\n")

# ================================================================================
# 处理更多验证集（示例）
# ================================================================================

# 如果有第二批、第三批验证集，可以继续使用相同模版：
#
# valid_path_2 <- "E:/RS/sm/耐药性分析/B/BATCH2/"
# validation_df_2 <- process_validation_set(valid_path_2, feature_mz, processing_params)
# write.csv(validation_df_2,
#           file = file.path(valid_path_2, 'peak_intensity_validation_batch2.csv'),
#           row.names = FALSE)

# ================================================================================
# 总结和验证
# ================================================================================

cat("\n" * 80, "\n")
cat("处理完成总结\n")
cat("=" * 80, "\n")
cat(sprintf("训练集:\n"))
cat(sprintf("  分组数: %d\n", nrow(train_df)))
cat(sprintf("  特征数: %d\n", ncol(train_df) - 1))
cat(sprintf("  输出文件: peak_intensity_train.csv\n"))

cat(sprintf("\n验证集:\n"))
cat(sprintf("  样本数: %d\n", nrow(validation_df_1)))
cat(sprintf("  特征数: %d\n", ncol(validation_df_1) - 1))
cat(sprintf("  输出文件: peak_intensity_validation.csv\n"))

cat(sprintf("\n特征一致性检查:\n"))
train_features <- colnames(train_df)[-1]
valid_features <- colnames(validation_df_1)[-1]
if (all(train_features == valid_features)) {
  cat("  ✓ 训练集和验证集特征完全一致!\n")
} else {
  cat("  ✗ 警告: 特征不一致!\n")
}

cat("\n所有处理完成!\n")
cat("=" * 80, "\n")
