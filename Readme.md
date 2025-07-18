# 问答组

## Clone

```bash
git clone https://github.com/L1ndenbaum/rag-based-llm-crop-chat.git
```

## Environment

### Environment Variables

```bash
echo "export DIFY_API_KEY=your-dify-api-key" >> ~/.bashrc
echo "export natappauthtoken=your-natapp-authtoken" >> ~/.bashrc
source ~/.bashrc
```

### npm

```bash
cd crop-chat-app/client
npm install
```

### python

```bash
python -m venv your-venv-name
source your-venv-name/bin/activate
cd crop-chat-app/server
pip install -r requirements.txt
```

## Build

```bash
cd crop-chat-app/client
chmod +x ./build.sh
./build.sh
```

## Run

```bash
chmod +x ./natapp
./natapp -authtoken=$natappauthtoken
cd crop-chat-app/server
python app.py
```

## Natapp内网穿透简单部署

访问[Natapp官网](https://natapp.cn/)
在crop-chat-app/client/.env.local中，设置你的Natapp Tunnel地址。
