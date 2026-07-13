package com.easymeeting.websocket.netty;

import com.easymeeting.entity.constants.Constants;
import com.easymeeting.entity.dto.MessageSendDto;
import com.easymeeting.entity.dto.PeerConnectionDataDto;
import com.easymeeting.entity.dto.PeerMessageDto;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.MessageSend2TypeEnum;
import com.easymeeting.entity.enums.MessageTypeEnum;
import com.easymeeting.redis.RedisComponet;
import com.easymeeting.service.MeetingInfoService;
import com.easymeeting.utils.JsonUtils;
import com.easymeeting.websocket.message.MessageHandler;
import io.netty.channel.Channel;
import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.handler.codec.http.websocketx.TextWebSocketFrame;
import io.netty.util.Attribute;
import io.netty.util.AttributeKey;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

/**
 * @Description ws 业务处理
 * @Author 程序员老罗
 * @Date 2023/12/17 10:10
 */

/**
 * 设置通道共享
 */
@ChannelHandler.Sharable
@Component("handlerWebSocket")
public class HandlerWebSocket extends SimpleChannelInboundHandler<TextWebSocketFrame> {

    private static final Logger logger = LoggerFactory.getLogger(HandlerWebSocket.class);

    @Resource
    private MeetingInfoService meetingInfoService;

    @Resource
    private RedisComponet redisComponet;

    @Resource
    private MessageHandler messageHandler;

    /**
     * 当通道就绪后会调用此方法，通常我们会在这里做一些初始化操作
     *
     * @param ctx
     * @throws Exception
     */
    @Override
    public void channelActive(ChannelHandlerContext ctx) throws Exception {
        // Channel channel = ctx.channel();
        logger.info("有新的连接加入。。。");
    }

    /**
     * 当通道不再活跃时（连接关闭）会调用此方法，我们可以在这里做一些清理工作
     *
     * @param ctx
     * @throws Exception
     */
    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        logger.info("有连接已经断开。。。");
        meetingInfoService.removeContext(ctx.channel());
    }

    /**
     * 读就绪事件 当有消息可读时会调用此方法，我们可以在这里读取消息并处理。
     *
     * @param ctx
     * @param textWebSocketFrame
     * @throws Exception
     */
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, TextWebSocketFrame textWebSocketFrame) {
        //接收心跳
        //logger.info("收到消息:{}", textWebSocketFrame.text());
        String text = textWebSocketFrame.text();
        if (Constants.PING.equals(text)) {
            Channel channel = ctx.channel();
            Attribute<String> attribute = channel.attr(AttributeKey.valueOf(channel.id().toString()));
            String userId = attribute.get();
            redisComponet.saveUserHeartBeat(userId);
            return;
        }

        PeerConnectionDataDto dataDto = JsonUtils.convertJson2Obj(text, PeerConnectionDataDto.class);
        TokenUserInfoDto tokenUserInfoDto = redisComponet.getTokenUserInfoDto(dataDto.getToken());
        if (tokenUserInfoDto == null) {
            return;
        }
        MessageSendDto messageSendDto = new MessageSendDto();
        messageSendDto.setMessageType(MessageTypeEnum.PEER.getType());

        PeerMessageDto peerMessageDto = new PeerMessageDto();
        peerMessageDto.setSignalType(dataDto.getSignalType());
        peerMessageDto.setSignalData(dataDto.getSignalData());

        messageSendDto.setMessageContent(peerMessageDto);
        messageSendDto.setMeetingId(tokenUserInfoDto.getCurrentMeetingId());
        messageSendDto.setSendUserId(tokenUserInfoDto.getUserId());
        messageSendDto.setReceiveUserId(dataDto.getReceiveUserId());
        messageSendDto.setMessageSend2Type(MessageSend2TypeEnum.USER.getType());
        messageHandler.sendMessage(messageSendDto);
    }
}