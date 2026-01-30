# 安装必需的R包

# 设置镜像
options(repos = c(CRAN = "https://cloud.r-project.org/"))

cat("开始安装R包...\n")

# 安装BiocManager
if (!requireNamespace("BiocManager", quietly = TRUE)) {
    cat("安装 BiocManager...\n")
    install.packages("BiocManager", quiet = TRUE)
}

# 安装MALDIquant (从CRAN)
if (!requireNamespace("MALDIquant", quietly = TRUE)) {
    cat("安装 MALDIquant...\n")
    install.packages("MALDIquant", quiet = TRUE)
}

# 安装MALDIquantForeign (从CRAN)
if (!requireNamespace("MALDIquantForeign", quietly = TRUE)) {
    cat("安装 MALDIquantForeign...\n")
    install.packages("MALDIquantForeign", quiet = TRUE)
}

# 安装readxl
if (!requireNamespace("readxl", quietly = TRUE)) {
    cat("安装 readxl...\n")
    install.packages("readxl", quiet = TRUE)
}

cat("\n所有R包安装完成！\n")
cat("已安装的包:\n")
cat("  - MALDIquant:", as.character(packageVersion("MALDIquant")), "\n")
cat("  - MALDIquantForeign:", as.character(packageVersion("MALDIquantForeign")), "\n")
cat("  - readxl:", as.character(packageVersion("readxl")), "\n")

