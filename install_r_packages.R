# 安装必需的R包

# 创建用户库目录
user_lib <- Sys.getenv("R_LIBS_USER")
if (user_lib == "") {
    user_lib <- path.expand("~/R/library")
}
if (!dir.exists(user_lib)) {
    dir.create(user_lib, recursive = TRUE)
    cat("创建用户库目录:", user_lib, "\n")
}

# 设置库路径
.libPaths(c(user_lib, .libPaths()))

# 设置镜像
options(repos = c(CRAN = "https://cloud.r-project.org/"))

cat("R库路径:", .libPaths(), "\n")
cat("开始安装R包...\n\n")

# 安装MALDIquant
if (!requireNamespace("MALDIquant", quietly = TRUE)) {
    cat("安装 MALDIquant...\n")
    tryCatch({
        install.packages("MALDIquant", lib = user_lib, dependencies = TRUE)
        cat("  ✓ MALDIquant 安装成功\n")
    }, error = function(e) {
        cat("  ✗ MALDIquant 安装失败:", conditionMessage(e), "\n")
    })
} else {
    cat("✓ MALDIquant 已安装\n")
}

# 安装MALDIquantForeign
if (!requireNamespace("MALDIquantForeign", quietly = TRUE)) {
    cat("\n安装 MALDIquantForeign...\n")
    tryCatch({
        install.packages("MALDIquantForeign", lib = user_lib, dependencies = TRUE)
        cat("  ✓ MALDIquantForeign 安装成功\n")
    }, error = function(e) {
        cat("  ✗ MALDIquantForeign 安装失败:", conditionMessage(e), "\n")
    })
} else {
    cat("✓ MALDIquantForeign 已安装\n")
}

# 安装readxl（不强制依赖，如果失败也继续）
if (!requireNamespace("readxl", quietly = TRUE)) {
    cat("\n安装 readxl...\n")
    tryCatch({
        install.packages("readxl", lib = user_lib, dependencies = FALSE)
        cat("  ✓ readxl 安装成功\n")
    }, error = function(e) {
        cat("  ✗ readxl 安装失败:", conditionMessage(e), "\n")
        cat("  尝试不安装依赖...\n")
        tryCatch({
            install.packages("readxl", lib = user_lib, dependencies = NA)
            cat("  ✓ readxl 安装成功（无依赖）\n")
        }, error = function(e2) {
            cat("  ✗ readxl 仍然失败，跳过\n")
        })
    })
} else {
    cat("✓ readxl 已安装\n")
}

cat("\n")
cat(paste(rep("=", 50), collapse=""))
cat("\n安装完成！已安装的包:\n")
cat(paste(rep("=", 50), collapse=""))
cat("\n\n")

installed_count <- 0
if (requireNamespace("MALDIquant", quietly = TRUE)) {
    v <- as.character(packageVersion("MALDIquant"))
    cat("  ✓ MALDIquant:", v, "\n")
    installed_count <- installed_count + 1
}
if (requireNamespace("MALDIquantForeign", quietly = TRUE)) {
    v <- as.character(packageVersion("MALDIquantForeign"))
    cat("  ✓ MALDIquantForeign:", v, "\n")
    installed_count <- installed_count + 1
}
if (requireNamespace("readxl", quietly = TRUE)) {
    v <- as.character(packageVersion("readxl"))
    cat("  ✓ readxl:", v, "\n")
    installed_count <- installed_count + 1
}

cat("\n")
if (installed_count >= 2) {
    cat("✅ 核心包已安装，可以开始使用！\n")
    if (installed_count < 3) {
        cat("⚠️ readxl未安装，请手动上传Excel文件内容\n")
    }
} else {
    cat("❌ 关键包安装失败，无法使用\n")
    quit(status = 1)
}

