// 飞书机器人测试脚本
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
