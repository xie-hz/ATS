package com.easymeeting.websocket.test;

import com.rabbitmq.client.*;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class RabbitmqSubscriber {
    private static final String EXCHANGE_NAME = "fanout_exchange";

    private static final int MAX_RETRIES = 3;

    private static final String RETRY_COUNT_KEY = "retryCount";

    public static void main(String[] argv) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        factory.setPort(5672);
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.FANOUT);
        String queueName = channel.queueDeclare().getQueue();
        channel.queueBind(queueName, EXCHANGE_NAME, "");

        // 关闭自动确认
        boolean autoAck = false;
        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            try {
                String message = new String(delivery.getBody(), "UTF-8");
                System.out.println("收到消息->" + message + System.currentTimeMillis());
                // 模拟处理失败
                if (Math.random() > 0.3) {
                    throw new RuntimeException("模拟处理失败");
                }
                // 处理成功，手动确认
                channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
            } catch (Exception e) {
                System.out.println("处理失败: " + e.getMessage());
                handleFailedMessage(channel, delivery, queueName);
            }
        };
        channel.basicConsume(queueName, autoAck, deliverCallback, consumerTag -> {
        });
        System.out.println("订阅已启动，等待消息中.....");
    }

    private static void handleFailedMessage(Channel channel, Delivery delivery, String queueName) throws IOException {
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
            System.out.println("超过最大重试次数，放弃处理");
            channel.basicReject(delivery.getEnvelope().getDeliveryTag(), false);
        }
    }
}
