package com.easymeeting.websocket.message;

import com.easymeeting.entity.constants.Constants;
import com.easymeeting.entity.dto.MessageSendDto;
import com.easymeeting.utils.JsonUtils;
import com.easymeeting.websocket.ChannelContextUtils;
import com.rabbitmq.client.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import javax.annotation.PreDestroy;
import javax.annotation.Resource;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeoutException;

@Slf4j
@Component
@ConditionalOnProperty(name = Constants.MESSAGEING_HANDLE_CHANNEL_KEY, havingValue = Constants.MESSAGEING_HANDLE_CHANNEL_RABBITMQ)
public class MessageHandler4Rabbitmq implements MessageHandler {

    private static final String EXCHANGE_NAME = "fanout_exchange";

    private static final int MAX_RETRIES = 3;

    private static final String RETRY_COUNT_KEY = "retryCount";

    @Resource
    private ChannelContextUtils channelContextUtils;

    @Value("${rabbitmq.host:}")
    private String host;

    @Value("${rabbitmq.port:}")
    private Integer port;

    private ConnectionFactory factory;

    private Connection connection;

    private Channel channel;

    @Override
    public void listenMessage() {
        factory = new ConnectionFactory();
        factory.setHost(host);
        factory.setPort(port);
        try {
            connection = factory.newConnection();
            channel = connection.createChannel();
            channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.FANOUT);
            String queueName = channel.queueDeclare().getQueue();
            channel.queueBind(queueName, EXCHANGE_NAME, "");
            // 关闭自动确认
            boolean autoAck = false;
            DeliverCallback deliverCallback = (consumerTag, delivery) -> {
                try {
                    String message = new String(delivery.getBody(), "UTF-8");
                    log.info("rabbitmq收到消息:{}", message);
                    channelContextUtils.sendMessage(JsonUtils.convertJson2Obj(message, MessageSendDto.class));
                    // 处理成功，手动确认
                    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
                } catch (Exception e) {
                    log.error("rabbitmq 处理消息失败", e);
                    handleFailedMessage(channel, delivery, queueName);
                }
            };
            channel.basicConsume(queueName, autoAck, deliverCallback, consumerTag -> {
            });
        } catch (Exception e) {
            log.error("rabbitmq 监听消息失败", e);
        }
    }

    private void handleFailedMessage(Channel channel, Delivery delivery, String queueName) throws IOException {
        Map<String, Object> headers = delivery.getProperties().getHeaders();
        if (headers == null) {
            headers = new HashMap();
        }
        Integer retryCount = 0;
        if (headers.containsKey(RETRY_COUNT_KEY)) {
            retryCount = (Integer) headers.get(RETRY_COUNT_KEY);
        }
        if (retryCount < MAX_RETRIES - 1) {
            // 增加重试计数并重新发布
            headers.put(RETRY_COUNT_KEY, retryCount + 1);
            AMQP.BasicProperties props = new AMQP.BasicProperties.Builder().headers(headers).build();
            channel.basicPublish("", queueName, props, delivery.getBody());
            channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        } else {
            // 超过最大重试次数，转入死信队列或记录日志
            log.info("超过最大重试次数，放弃处理");
            channel.basicReject(delivery.getEnvelope().getDeliveryTag(), false);
        }
    }

    @Override
    public void sendMessage(MessageSendDto sendDto) {
        try (Connection connection = factory.newConnection(); Channel channel = connection.createChannel()) {
            channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.FANOUT);
            channel.basicPublish(EXCHANGE_NAME, "", null, JsonUtils.convertObj2Json(sendDto).getBytes());
        } catch (Exception e) {
            log.error("rabbitmq发送消息失败");
        }
    }

    @PreDestroy
    public void destroy() throws IOException, TimeoutException {
        if (channel != null && channel.isOpen()) {
            channel.close();
        }
        if (connection != null && connection.isOpen()) {
            connection.close();
        }
    }
}
