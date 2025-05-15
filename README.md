# 拼好图项目启动指南

## 环境要求
1. Python 3.8+ 
2. pip 包管理工具

## 安装步骤
1. 克隆项目仓库
2. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```
3. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 启动项目
1. 确保虚拟环境已激活
2. 运行以下命令启动服务：
   ```bash
   python app.py
   ```
3. 打开浏览器访问：http://localhost:5000

## 项目结构
- `app.py`: 主程序入口
- `templates/`: HTML模板文件
- `uploads/`: 用户上传文件存储目录

## 注意事项
1. 确保uploads目录具有写权限
2. 开发环境建议使用DEBUG模式