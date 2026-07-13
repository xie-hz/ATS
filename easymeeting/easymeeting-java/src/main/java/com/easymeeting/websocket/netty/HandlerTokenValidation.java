package com.easymeeting.websocket.netty;

import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.redis.RedisComponet;
import com.easymeeting.utils.StringTools;
import com.easymeeting.websocket.ChannelContextUtils;
import io.netty.buffer.Unpooled;
import io.netty.channel.ChannelFutureListener;
import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.handler.codec.http.*;
import io.netty.util.CharsetUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;

@ChannelHandler.Sharable
@Component
@Slf4j
public class HandlerTokenValidation extends SimpleChannelInboundHandler<FullHttpRequest> {

    @Resource
    private ChannelContextUtils channelContextUtils;

    @Resource
    private RedisComponet redisComponet;

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest request) {
        String uri = request.uri();
        QueryStringDecoder queryDecoder = new QueryStringDecoder(uri);
        List<String> tokens = queryDecoder.parameters().get("token");
        List<String> reconnect = queryDecoder.parameters().get("reconnect");
        if (tokens == null) {
            sendErrorResponse(ctx);
            return;
        }
        String token = tokens.get(0);
        //这里是优化后的重连机制，ws断开后会将用户的会议信息清除，所以重连后从临时信息中获取token信息
        TokenUserInfoDto tokenUserInfoDto = null;
        if (reconnect != null && Boolean.parseBoolean(reconnect.get(0))) {
            log.info("重连中。。。");
            //判断临时token信息
            tokenUserInfoDto = redisComponet.getTokenUserInfoDtoFromTemp(token);
            if (tokenUserInfoDto != null) {
                //如果临时缓存有，说明是重连，设置到正式缓存信息中
                redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
            }
        } else {
            tokenUserInfoDto = checkToken(token);
        }
        if (tokenUserInfoDto == null) {
            log.error("校验token失败:{}", token);
            sendErrorResponse(ctx);
            return;
        }
        // 如果需要转发消息  增加引用计数
        ctx.fireChannelRead(request.retain());
        //加入通道
        channelContextUtils.addContext(tokenUserInfoDto.getUserId(), ctx.channel());
    }

    private TokenUserInfoDto checkToken(String token) {
        if (StringTools.isEmpty(token)) {
            return null;
        }
        TokenUserInfoDto tokenUserInfoDto = redisComponet.getTokenUserInfoDto(token);
        return tokenUserInfoDto;
    }

    private void sendErrorResponse(ChannelHandlerContext ctx) {
        FullHttpResponse response = new DefaultFullHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.FORBIDDEN, Unpooled.copiedBuffer("token无效", CharsetUtil.UTF_8));
        response.headers().set(HttpHeaderNames.CONTENT_TYPE, "text/plain; charset=UTF-8");
        response.headers().set(HttpHeaderNames.CONTENT_LENGTH, response.content().readableBytes());
        ctx.writeAndFlush(response).addListener(ChannelFutureListener.CLOSE);
    }
}