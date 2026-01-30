# 安装必需的R包
install.packages("BiocManager", repos = "https://cran.rstudio.com/")

# 安装MALDIquant相关包
BiocManager::install("MALDIquant", update = FALSE, ask = FALSE)
BiocManager::install("MALDIquantForeign", update = FALSE, ask = FALSE)

# 安装readxl
install.packages("readxl", repos = "https://cran.rstudio.com/")

cat("R packages installed successfully!\n")
