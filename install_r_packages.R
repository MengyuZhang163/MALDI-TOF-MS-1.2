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

# 安装依赖包
dependencies <- c("XML", "base64enc")
for (pkg in dependencies) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
        cat(paste0("安装依赖包 ", pkg, "...\n"))
        tryCatch({
            install.packages(pkg, lib = user_lib, dependencies = TRUE)
            cat(paste0("  ✓ ", pkg, " 安装成功\n"))
        }, error = function(e) {
            cat(paste0("  ✗ ", pkg, " 安装失败: ", e$message, "\n"))
        })
    }
}

# 安装MALDIquant
if (!requireNamespace("MALDIquant", quietly = TRUE)) {
    cat("\n安装 MALDIquant...\n")
    tryCatch({
        install.packages("MALDIquant", lib = user_lib, dependencies = TRUE)
        cat("  ✓ MALDIquant 安装成功\n")
    }, error = function(e) {
        cat(paste0("  ✗ MALDIquant 安装失败: ", e$message, "\n"))
    })
} else {
    cat("\n✓ MALDIquant 已安装\n")
}

# 安装MALDIquantForeign
if (!requireNamespace("MALDIquantForeign", quietly = TRUE)) {
    cat("\n安装 MALDIquantForeign...\n")
    tryCatch({
        install.packages("MALDIquantForeign", lib = user_lib, dependencies = TRUE)
        cat("  ✓ MALDIquantForeign 安装成功\n")
    }, error = function(e) {
        cat(paste0("  ✗ MALDIquantForeign 安装失败: ", e$message, "\n"))
    })
} else {
    cat("\n✓ MALDIquantForeign 已安装\n")
}

# 安装readxl
if (!requireNamespace("readxl", quietly = TRUE)) {
    cat("\n安装 readxl...\n")
    tryCatch({
        install.packages("readxl", lib = user_lib, dependencies = TRUE)
        cat("  ✓ readxl 安装成功\n")
    }, error = function(e) {
        cat(paste0("  ✗ readxl 安装失败: ", e$message, "\n"))
    })
} else {
    cat("\n✓ readxl 已安装\n")
}

cat("\n" + paste(rep("=", 50), collapse="") + "\n")
cat("安装完成！已安装的包:\n")
cat(paste(rep("=", 50), collapse="") + "\n\n")

installed_packages <- c()
if (requireNamespace("MALDIquant", quietly = TRUE)) {
    v <- as.character(packageVersion("MALDIquant"))
    cat("  ✓ MALDIquant:", v, "\n")
    installed_packages <- c(installed_packages, "MALDIquant")
}
if (requireNamespace("MALDIquantForeign", quietly = TRUE)) {
    v <- as.character(packageVersion("MALDIquantForeign"))
    cat("  ✓ MALDIquantForeign:", v, "\n")
    installed_packages <- c(installed_packages, "MALDIquantForeign")
}
if (requireNamespace("readxl", quietly = TRUE)) {
    v <- as.character(packageVersion("readxl"))
    cat("  ✓ readxl:", v, "\n")
    installed_packages <- c(installed_packages, "readxl")
}

if (length(installed_packages) == 3) {
    cat("\n✅ 所有必需包已成功安装！\n")
} else {
    cat("\n⚠️ 部分包安装失败，请检查错误信息\n")
    quit(status = 1)
}

