package com.easymeeting.websocket;

import com.alibaba.fastjson.JSON;
import com.easymeeting.entity.dto.MeetingExitDto;
import com.easymeeting.entity.dto.MeetingMemberDto;
import com.easymeeting.entity.dto.MessageSendDto;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.MeetingMemberStatusEnum;
import com.easymeeting.entity.enums.MessageSend2TypeEnum;
import com.easymeeting.entity.enums.MessageTypeEnum;
import com.easymeeting.entity.po.UserInfo;
import com.easymeeting.entity.query.UserInfoQuery;
import com.easymeeting.mappers.UserInfoMapper;
import com.easymeeting.redis.RedisComponet;
import com.easymeeting.utils.JsonUtils;
import com.easymeeting.utils.StringTools;
import io.netty.channel.Channel;
import io.netty.channel.group.ChannelGroup;
import io.netty.channel.group.DefaultChannelGroup;
import io.netty.handler.codec.http.websocketx.TextWebSocketFrame;
import io.netty.util.AttributeKey;
import io.netty.util.concurrent.GlobalEventExecutor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.stream.Collectors;

@Component("channelContextUtils")
@Slf4j
public class ChannelContextUtils {

    @Resource
    private RedisComponet redisComponet;

    @Resource
    private UserInfoMapper<UserInfo, UserInfoQuery> userInfoMapper;

    public static final ConcurrentMap<String, Channel> USER_CONTEXT_MAP = new ConcurrentHashMap();

    public static final ConcurrentMap<String, ChannelGroup> MEETING_ROOM_CONTEXT_MAP = new ConcurrentHashMap();


    private void sendMsg2Group(MessageSendDto messageSendDto) {
        if (messageSendDto.getMeetingId() == null) {
            return;
        }
        ChannelGroup group = MEETING_ROOM_CONTEXT_MAP.get(messageSendDto.getMeetingId());
        if (group == null) {
            return;
        }
        group.writeAndFlush(new TextWebSocketFrame(JSON.toJSONString(messageSendDto)));
        /**
         * 特殊处理，消息发送后处理相关channel,用户退出后，移除channel
         */
        if (MessageTypeEnum.EXIT_MEETING_ROOM.getType().equals(messageSendDto.getMessageType())) {
            MeetingExitDto exitDto = JsonUtils.convertJson2Obj((String) messageSendDto.getMessageContent(), MeetingExitDto.class);
            removeContextFromGroup(exitDto.getExitUserId(), messageSendDto.getMeetingId());
            List<MeetingMemberDto> meetingMemberDtoList = redisComponet.getMeetingMemberList(messageSendDto.getMeetingId());
            List<MeetingMemberDto> onlineMemberList =
                    meetingMemberDtoList.stream().filter(item -> MeetingMemberStatusEnum.NORMAL.getStatus().equals(item.getStatus())).collect(Collectors.toList());
            if (onlineMemberList.isEmpty()) {
                removeContextGroup(messageSendDto.getMeetingId());
            }
            return;
        }
        if (MessageTypeEnum.FINIS_MEETING.getType().equals(messageSendDto.getMessageType())) {
            List<MeetingMemberDto> meetingMemberDtoList = redisComponet.getMeetingMemberList(messageSendDto.getMeetingId());
            for (MeetingMemberDto meetingMemberDto : meetingMemberDtoList) {
                removeContextFromGroup(meetingMemberDto.getUserId(), messageSendDto.getMeetingId());
            }
            removeContextGroup(messageSendDto.getMeetingId());
        }
    }

    private void sendMsg2User(MessageSendDto messageSendDto) {
        if (messageSendDto.getReceiveUserId() == null) {
            return;
        }
        Channel channel = USER_CONTEXT_MAP.get(messageSendDto.getReceiveUserId());
        if (channel == null) {
            return;
        }
        channel.writeAndFlush(new TextWebSocketFrame(JSON.toJSONString(messageSendDto)));
        /**
         * 强制下线特殊处理
         */
        if (MessageTypeEnum.FORCE_OFF_LINE.getType().equals(messageSendDto.getMessageType())) {
            closeContext(messageSendDto.getReceiveUserId());
        }
    }

    public void closeContext(String userId) {
        if (StringTools.isEmpty(userId)) {
            return;
        }
        redisComponet.cleanUserTokenByUserId(userId);
        Channel channel = USER_CONTEXT_MAP.get(userId);
        USER_CONTEXT_MAP.remove(userId);
        if (channel != null) {
            channel.close();
        }
    }


    public void sendMessage(MessageSendDto messageSendDto) {
        if (MessageSend2TypeEnum.USER.getType().equals(messageSendDto.getMessageSend2Type())) {
            sendMsg2User(messageSendDto);
        } else {
            sendMsg2Group(messageSendDto);
        }
    }


    //用户移除群
    public void removeContextFromGroup(String userId, String meetingId) {
        Channel context = USER_CONTEXT_MAP.get(userId);
        if (null == context) {
            return;
        }
        ChannelGroup group = MEETING_ROOM_CONTEXT_MAP.get(meetingId);
        if (group != null) {
            group.remove(context);
        }
    }

    public void removeContextGroup(String meetingId) {
        MEETING_ROOM_CONTEXT_MAP.remove(meetingId);
    }

    public void removeContextUser(String userId) {
        USER_CONTEXT_MAP.remove(userId);
    }


    public void addContext(String userId, Channel channel) {
        try {
            String channelId = channel.id().toString();
            AttributeKey attributeKey = null;
            if (!AttributeKey.exists(channelId)) {
                attributeKey = AttributeKey.newInstance(channel.id().toString());
            } else {
                attributeKey = AttributeKey.valueOf(channel.id().toString());
            }
            channel.attr(attributeKey).set(userId);
            USER_CONTEXT_MAP.put(userId, channel);

            //更新最后登录时间，针对重连后更新最后登录时间
            UserInfo userInfo = new UserInfo();
            userInfo.setLastLoginTime(System.currentTimeMillis());
            userInfoMapper.updateByUserId(userInfo, userId);

            //如果在会议中，自动加入会议
            TokenUserInfoDto tokenUserInfoDto = redisComponet.getTokenUserInfoDtoByUserId(userId);
            if (tokenUserInfoDto.getCurrentMeetingId() == null) {
                return;
            }

            addMeetingRoom(tokenUserInfoDto.getCurrentMeetingId(), userId);
        } catch (Exception e) {
            log.error("初始化链接失败", e);
        }
    }

    /**
     * 加入会议室
     *
     * @param meetingId
     */
    public void addMeetingRoom(String meetingId, String userId) {
        Channel context = USER_CONTEXT_MAP.get(userId);
        if (null == context) {
            return;
        }
        ChannelGroup group = MEETING_ROOM_CONTEXT_MAP.get(meetingId);
        if (group == null) {
            group = new DefaultChannelGroup(GlobalEventExecutor.INSTANCE);
            MEETING_ROOM_CONTEXT_MAP.put(meetingId, group);
        }
        Channel channel = group.find(context.id());
        if (channel == null) {
            group.add(context);
        }
    }
}
