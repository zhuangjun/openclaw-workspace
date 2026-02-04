const fs = require('fs');
const path = require('path');

// 生成飞书配置模板
const larkConfigTemplate = {
  channels: {
    lark: {
      enabled: true,
      type: 'lark',
      app_id: process.env.LARK_APP_ID || 'YOUR_APP_ID_HERE',
      app_secret: process.env.LARK_APP_SECRET || 'YOUR_APP_SECRET_HERE',
      encrypt_key: process.env.LARK_ENCRYPT_KEY || '', // 可选
      verification_token: process.env.LARK_VERIFICATION_TOKEN || 'YOUR_VERIFICATION_TOKEN_HERE',
      port: 8080, // 用于接收飞书回调的端口
      webhook_path: '/lark/webhook'
    }
  }
};

// 写入配置文件
fs.writeFileSync(
  path.join(__dirname, 'lark_config.yaml'),
  `# OpenClaw 飞书集成配置文件
# 请将敏感信息替换为实际值

channels:
  lark:
    enabled: true
    type: lark
    app_id: "${process.env.LARK_APP_ID || 'YOUR_APP_ID_HERE'}"
    app_secret: "${process.env.LARK_APP_SECRET || 'YOUR_APP_SECRET_HERE'}"
    encrypt_key: "${process.env.LARK_ENCRYPT_KEY || ''}"  # 可选
    verification_token: "${process.env.LARK_VERIFICATION_TOKEN || 'YOUR_VERIFICATION_TOKEN_HERE'}"
    port: 8080  # 用于接收飞书回调的端口
    webhook_path: "/lark/webhook"
`
);

// 生成环境变量配置文件
fs.writeFileSync(
  path.join(__dirname, '.env.lark'),
  `# 飞书集成环境变量配置
# 请将占位符替换为实际值

LARK_APP_ID=YOUR_ACTUAL_APP_ID
LARK_APP_SECRET=YOUR_ACTUAL_APP_SECRET
LARK_ENCRYPT_KEY=YOUR_ENCRYPT_KEY_IF_SET
LARK_VERIFICATION_TOKEN=YOUR_VERIFICATION_TOKEN
`
);

// 生成安装和配置说明
fs.writeFileSync(
  path.join(__dirname, 'LARK_SETUP_GUIDE.md'),
  `# OpenClaw 飞书集成设置指南

## 步骤 1: 创建飞书应用

1. 访问 [飞书开发者平台](https://open.feishu.cn/)
2. 登录后点击"创建企业自建应用"
3. 填写应用信息（应用名称、描述等）
4. 创建完成后，在凭证与基础信息页面获取 App ID 和 App Secret

## 步骤 2: 配置机器人权限

1. 在应用管理页面，选择"机器人"
2. 编辑机器人的权限范围：
   - 发送消息给用户
   - 获取用户信息
   - 获取群组信息

## 步骤 3: 配置事件订阅

1. 在应用管理页面，选择"事件订阅"
2. 添加事件：选择"接收消息事件"(im.message.receive_v1)
3. 设置请求地址：\`http://your-server-ip:8080/lark/webhook\`
   - 如果有公网IP，直接使用服务器IP
   - 如果是本地开发，可使用内网穿透工具如 ngrok
4. 点击"验证并保存"，系统会向您发送一个验证请求

## 步骤 4: 更新配置

1. 编辑 \`lark_config.yaml\` 文件，填入真实的 App ID 和 App Secret
2. 或者将环境变量设置到 .env 文件中

## 步骤 5: 启动服务

重启 OpenClaw 服务使配置生效：

\`\`\`
openclaw gateway restart
\`\`\`

## 步骤 6: 测试连接

1. 在飞书中搜索您的机器人并发送消息
2. 观察 OpenClaw 日志确认收到消息
3. 验证机器人能否正常回复

## 安全注意事项

- 不要在版本控制系统中提交包含真实密钥的配置文件
- 定期更换 App Secret
- 使用 HTTPS 连接（生产环境推荐）
- 配置适当的防火墙规则
`
);

// 生成飞书机器人测试脚本
fs.writeFileSync(
  path.join(__dirname, 'lark_test.js'),
  `// 飞书机器人测试脚本
const axios = require('axios');

class LarkBotTester {
  constructor(appId, appSecret) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.token = null;
  }

  async getAccessToken() {
    try {
      const response = await axios.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
        app_id: this.appId,
        app_secret: this.appSecret
      });
      
      this.token = response.data.tenant_access_token;
      console.log('Access token obtained successfully');
      return this.token;
    } catch (error) {
      console.error('Failed to get access token:', error.response?.data || error.message);
      throw error;
    }
  }

  async sendMessageToUser(userId, message) {
    if (!this.token) {
      await this.getAccessToken();
    }

    try {
      const response = await axios.post('https://open.feishu.cn/open-apis/im/v1/messages', {
        receive_id_type: 'user_id',
        receive_id: userId,
        msg_type: 'text',
        content: JSON.stringify({ text: message })
      }, {
        headers: {
          'Authorization': 'Bearer ' + this.token,
          'Content-Type': 'application/json'
        }
      });

      console.log('Message sent successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to send message:', error.response?.data || error.message);
      throw error;
    }
  }
}

module.exports = LarkBotTester;
`
);

console.log('飞书集成配置文件已生成完成！');
console.log('- lark_config.yaml: OpenClaw 配置文件');
console.log('- .env.lark: 环境变量配置');
console.log('- LARK_SETUP_GUIDE.md: 详细设置指南');
console.log('- lark_test.js: 机器人测试脚本');