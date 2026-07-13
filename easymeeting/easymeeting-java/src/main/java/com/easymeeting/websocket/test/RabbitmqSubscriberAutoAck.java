package com.easymeeting.websocket.test;

import com.rabbitmq.client.*;

public class RabbitmqSubscriberAutoAck {
    private static final String EXCHANGE_NAME = "fanout_exchange";

    public static void main(String[] argv) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        factory.setPort(5672);
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.FANOUT);
        String queueName = channel.queueDeclare().getQueue();
        channel.queueBind(queueName, EXCHANGE_NAME, "");

        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            try {
                String message = new String(delivery.getBody(), "UTF-8");
                System.out.println("收到消息->" + message + System.currentTimeMillis());
                if (Math.random() > 0.3) {
                    throw new RuntimeException("模拟处理失败");
                }
            } catch (Exception e) {
                System.out.println("处理失败: " + e.getMessage());
            }
        };
        //第二个参数自动ack
        channel.basicConsume(queueName, true, deliverCallback, consumerTag -> {
        });
        System.out.println("订阅已启动，等待消息中.....");
    }
}
