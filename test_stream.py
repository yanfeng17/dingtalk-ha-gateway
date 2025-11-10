"""测试钉钉 Stream 连接"""

import asyncio
import logging
from dingtalk_stream import AckMessage, ChatbotHandler, ChatbotMessage, DingTalkStreamClient, Credential

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 填入你的凭证
CLIENT_ID = "ding3gutoniseoh80z4j"
CLIENT_SECRET = "hXtOnx__re3Lsk6ostRbwRtWtxdfJJPJb9h-fTUviWQsja0M1xch-xl8eM5Q9AiW"


class TestHandler(ChatbotHandler):
    """测试消息处理器"""
    
    async def process(self, callback_message):
        logger.info(f"✅ 收到消息!")
        # 解析消息
        msg = ChatbotMessage.from_dict(callback_message.data)
        logger.info(f"发送者: {msg.sender_nick}")
        logger.info(f"内容: {msg.text.content if msg.text else 'N/A'}")
        return AckMessage.STATUS_OK, "OK"


async def main():
    try:
        logger.info("开始测试 Stream 连接...")
        logger.info(f"Client ID: {CLIENT_ID[:10]}...")
        
        # 创建凭证
        credential = Credential(CLIENT_ID, CLIENT_SECRET)
        logger.info("✓ 凭证创建成功")
        
        # 创建 Stream 客户端
        stream_client = DingTalkStreamClient(credential)
        logger.info("✓ Stream 客户端创建成功")
        
        # 注册消息处理器（需要指定 topic）
        stream_client.register_callback_handler(ChatbotMessage.TOPIC, TestHandler())
        logger.info("✓ 消息处理器注册成功")
        
        # 开始连接
        logger.info("正在连接钉钉服务器...")
        logger.info("如果连接成功，会自动保持运行状态")
        logger.info("按 Ctrl+C 停止测试")
        logger.info("")
        logger.info("现在可以在钉钉中给机器人发消息测试！")
        
        await stream_client.start()
        
    except ImportError as e:
        logger.error("❌ dingtalk-stream SDK 未安装!")
        logger.error("请运行: pip install dingtalk-stream>=0.8.0")
        logger.error(f"详细错误: {e}")
    except Exception as e:
        logger.error(f"❌ Stream 连接失败: {e}")
        logger.error("请检查:")
        logger.error("1. Client ID 和 Client Secret 是否正确")
        logger.error("2. 网络连接是否正常")
        logger.error("3. 应用是否已发布并启用")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("测试停止")
    except Exception as e:
        logger.error(f"测试失败: {e}")
