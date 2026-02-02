# 📊 机器学习全能分析平台 (CV + External Validation)

一个功能强大的机器学习模型训练与验证平台，支持交叉验证和外部验证集评估。

## ✨ 核心功能

### 🎯 双重验证机制
- **内部验证 (Cross-Validation)**：使用分层K折交叉验证评估模型泛化能力
- **外部验证 (External Validation)**：在独立验证集上测试模型性能

### 🤖 支持的模型
- Random Forest (RF)
- XGBoost (XGB)
- Logistic Regression (LR)
- Support Vector Machine (SVM)
- K-Nearest Neighbors (KNN)
- Decision Tree (DT)
- AdaBoost
- Naive Bayes (NB)

### 📈 评估指标
- ROC-AUC 曲线
- PR 曲线
- 混淆矩阵
- Sensitivity / Specificity
- F1 Score
- DeLong 检验（统计学显著性）

### 🔬 高级功能
- ✅ 网格搜索调参 (GridSearchCV)
- ✅ 特征重要性可视化
- ✅ 模型自动筛选（基于 DeLong P 值）
- ✅ 相关系数分析
- ✅ 标准化预处理

## 🚀 快速开始

### 前置要求
- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   streamlit run app.py
   ```

4. **访问应用**
   打开浏览器访问 `http://localhost:8501`

## 📁 数据格式要求

### CSV 文件结构
```
Label, ID, Feature1, Feature2, Feature3, ...
1, Patient001, 23.5, 45.2, 67.8, ...
0, Patient002, 21.3, 43.1, 65.4, ...
```

### 重要说明
- **第1列**：标签 (Label)，二分类（0或1）
- **第2列**：样本ID
- **第3列及以后**：特征列
- 训练集和验证集的**列名必须一致**
- 验证集可以缺少某些特征（会自动补0）

### 示例数据
```csv
Label,ID,Age,BMI,Glucose,BloodPressure
1,P001,45,28.5,120,140
0,P002,38,24.2,95,120
1,P003,52,31.1,135,150
```

## 📖 使用指南

### 步骤 1: 上传数据
1. 在左侧边栏点击 **"1️⃣ 训练集 (Train)"** 上传训练数据
2. （可选）点击 **"2️⃣ 验证集 (External Val)"** 上传外部验证集

### 步骤 2: 配置参数
- **启用网格调参**：开启后会自动搜索最优超参数（耗时更长）
- **交叉验证折数**：建议 5-10 折
- **显著性水平**：用于模型筛选，默认 0.05

### 步骤 3: 运行分析
1. 点击 **🚀 开始运行** 按钮
2. 等待训练完成（首次运行会缓存）

### 步骤 4: 查看结果
- **Tab 1 - 内部验证**：查看交叉验证结果、特征重要性
- **Tab 2 - 外部验证**：查看独立验证集性能（如果提供）

## 📊 结果解读

### 性能评估表
- **Status**：✅保留 / ❌筛除（基于DeLong检验）
- **AUC (ROC)**：越接近1越好
- **P-value**：与最佳模型比较的显著性（<0.05 表示显著差异）
- **Correlation**：与最佳模型预测概率的相关性

### ROC 曲线
- 实线：保留的模型
- 虚线：被筛除的模型

### 混淆矩阵
展示保留模型的分类详情（TP, TN, FP, FN）

## 🔧 部署到 Streamlit Cloud

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **创建 Streamlit Cloud 应用**
   - 访问 [streamlit.io/cloud](https://streamlit.io/cloud)
   - 连接 GitHub 仓库
   - 选择主文件：`app.py`
   - 点击 Deploy

3. **等待部署完成**
   - 首次部署约需 3-5 分钟
   - 部署成功后会获得公开访问链接

## 📂 项目结构

```
.
├── app.py                  # 主应用文件
├── requirements.txt        # Python 依赖
├── packages.txt           # 系统依赖（可选）
├── .streamlit/
│   └── config.toml        # Streamlit 配置
├── README.md              # 本文档
└── .gitignore             # Git 忽略文件
```

## 🐛 常见问题

### Q1: 模型训练很慢？
**A**: 
- 关闭"网格调参"功能
- 减少交叉验证折数（如改为3折）
- 减少训练集样本数

### Q2: 内存不足？
**A**:
- 减少特征数量
- 使用特征选择
- 增加 Streamlit Cloud 内存限额

### Q3: 验证集列不匹配？
**A**:
- 确保验证集包含训练集的主要特征
- 缺失的特征会自动填充为0
- 检查列名是否完全一致（区分大小写）

### Q4: DeLong 检验 P 值为 1.0？
**A**:
- P=1.0 表示该模型是当前最佳模型（参考模型）
- 其他模型的 P 值是与该模型比较得出的

### Q5: 所有模型 AUC 都很低 (<0.6)？
**A**:
- 检查数据质量和特征工程
- 确认标签是否正确
- 尝试特征标准化（对SVM/LR尤为重要）

## 🎨 自定义配置

### 修改主题颜色
编辑 `.streamlit/config.toml`：
```toml
[theme]
primaryColor = "#FF6B6B"  # 修改为你喜欢的颜色
```

### 调整模型列表
编辑 `app.py` 的 `models_config` 字典：
```python
models_config = {
    'RF': (...),
    # 添加或删除模型
}
```

## 📊 性能优化建议

1. **启用缓存**：已自动启用 `@st.cache_data`
2. **并行计算**：部分模型支持 `n_jobs=-1`
3. **增量训练**：对大数据集使用 SGD 模型
4. **特征选择**：使用特征重要性过滤低贡献特征

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

## 📮 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

## 🙏 致谢

- Streamlit 团队提供的优秀框架
- scikit-learn 和 XGBoost 开发者
- DeLong 检验算法的原作者

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**
