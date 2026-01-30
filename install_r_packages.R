# 安装必需的R包

# 创建用户库目录
user_lib <- Sys.getenv("R_LIBS_USER")
if (!dir.exists(user_lib)) {
    dir.create(user_lib, recursive = TRUE)
}

# 设置库路径
.libPaths(c(user_lib, .libPaths()))

# 设置镜像
options(repos = c(CRAN = "https://cloud.r-project.org/"))

cat("R库路径:", .libPaths(), "\n")
cat("开始安装R包...\n")

# 安装MALDIquant (从CRAN)
if (!requireNamespace("MALDIquant", quietly = TRUE)) {
    cat("安装 MALDIquant...\n")
    install.packages("MALDIquant", lib = user_lib, quiet = TRUE)
}

# 安装MALDIquantForeign (从CRAN)
if (!requireNamespace("MALDIquantForeign", quietly = TRUE)) {
    cat("安装 MALDIquantForeign...\n")
    install.packages("MALDIquantForeign", lib = user_lib, quiet = TRUE)
}

# 安装readxl
if (!requireNamespace("readxl", quietly = TRUE)) {
    cat("安装 readxl...\n")
    install.packages("readxl", lib = user_lib, quiet = TRUE)
}

cat("\n所有R包安装完成！\n")
cat("已安装的包:\n")
if (requireNamespace("MALDIquant", quietly = TRUE)) {
    cat("  - MALDIquant:", as.character(packageVersion("MALDIquant")), "\n")
}
if (requireNamespace("MALDIquantForeign", quietly = TRUE)) {
    cat("  - MALDIquantForeign:", as.character(packageVersion("MALDIquantForeign")), "\n")
}
if (requireNamespace("readxl", quietly = TRUE)) {
    cat("  - readxl:", as.character(packageVersion("readxl")), "\n")
}

