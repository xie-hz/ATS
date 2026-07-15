package com.easymeeting.redis;

import com.easymeeting.entity.constants.Constants;
import com.easymeeting.entity.dto.MeetingMemberDto;
import com.easymeeting.entity.dto.SysSettingDto;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.MeetingMemberStatusEnum;
import com.easymeeting.utils.StringTools;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Component
@Slf4j
public class RedisComponet {
    @Resource
    private RedisUtils redisUtils;

    public String saveCheckCode(String code) {
        String checkCodeKey = UUID.randomUUID().toString();
        redisUtils.setex(Constants.REDIS_KEY_CHECK_CODE + checkCodeKey, code, 60 * 10);
        return checkCodeKey;
    }

    public String getCheckCode(String checkCodeKey) {
        return (String) redisUtils.get(Constants.REDIS_KEY_CHECK_CODE + checkCodeKey);
    }

    public void cleanCheckCode(String checkCodeKey) {
        redisUtils.delete(Constants.REDIS_KEY_CHECK_CODE + checkCodeKey);
    }

    /**
     * 获取token信息
     *
     * @param token
     * @return
     */
    public TokenUserInfoDto getTokenUserInfoDto(String token) {
        TokenUserInfoDto tokenUserInfoDto = (TokenUserInfoDto) redisUtils.get(Constants.REDIS_KEY_WS_TOKEN + token);
        return tokenUserInfoDto;
    }

    public void saveTokenUserInfoDto(TokenUserInfoDto tokenUserInfoDto) {
        redisUtils.setex(Constants.REDIS_KEY_WS_TOKEN + tokenUserInfoDto.getToken(), tokenUserInfoDto, Constants.REDIS_KEY_EXPIRES_DAY * 2);
        redisUtils.setex(Constants.REDIS_KEY_WS_TOKEN_USERID + tokenUserInfoDto.getUserId(), tokenUserInfoDto.getToken(), Constants.REDIS_KEY_EXPIRES_DAY * 2);
    }

    /**
     * 保存访客 Token（短 TTL，10 分钟过期）
     */
    public void saveGuestTokenUserInfoDto(TokenUserInfoDto tokenUserInfoDto) {
        redisUtils.setex(Constants.REDIS_KEY_WS_TOKEN + tokenUserInfoDto.getToken(), tokenUserInfoDto, Constants.REDIS_KEY_EXPIRES_GUEST_TOKEN);
        redisUtils.setex(Constants.REDIS_KEY_WS_TOKEN_USERID + tokenUserInfoDto.getUserId(), tokenUserInfoDto.getToken(), Constants.REDIS_KEY_EXPIRES_GUEST_TOKEN);
    }

    public TokenUserInfoDto getTokenUserInfoDtoByUserId(String userId) {
        String token = (String) redisUtils.get(Constants.REDIS_KEY_WS_TOKEN_USERID + userId);
        if (StringTools.isEmpty(token)) {
            return null;
        }
        return getTokenUserInfoDto(token);
    }


    /**
     * 清除token信息
     *
     * @param userId
     */
    public void cleanUserTokenByUserId(String userId) {
        String token = (String) redisUtils.get(Constants.REDIS_KEY_WS_TOKEN_USERID + userId);
        if (!StringTools.isEmpty(token)) {
            redisUtils.delete(Constants.REDIS_KEY_WS_TOKEN + token);
        }
        redisUtils.delete(Constants.REDIS_KEY_WS_TOKEN_USERID + userId);
        removeUserHeartBeat(userId);
    }

    //保存用户临时信息
    public void saveTokenUserInfoDtoTemp(TokenUserInfoDto tokenUserInfoDto) {
        redisUtils.setex(Constants.REDIS_KEY_WS_TOKEN_TEMP + tokenUserInfoDto.getToken(), tokenUserInfoDto, Constants.REDIS_KEY_EXPIRES_ONE_MIN);
    }

    public TokenUserInfoDto getTokenUserInfoDtoFromTemp(String token) {
        return (TokenUserInfoDto) redisUtils.get(Constants.REDIS_KEY_WS_TOKEN_TEMP + token);
    }

    //保存最后心跳时间
    public void saveUserHeartBeat(String userId) {
        redisUtils.setex(Constants.REDIS_KEY_WS_USER_HEART_BEAT + userId, System.currentTimeMillis(), Constants.REDIS_KEY_EXPIRES_HEART_BEAT);
    }

    //删除用户心跳
    public void removeUserHeartBeat(String userId) {
        redisUtils.delete(Constants.REDIS_KEY_WS_USER_HEART_BEAT + userId);
    }


    //获取用户心跳
    public Long getUserHeartBeat(String userId) {
        return (Long) redisUtils.get(Constants.REDIS_KEY_WS_USER_HEART_BEAT + userId);
    }


    /**
     * 加入会议
     *
     * @param meetingId
     * @param meetingMemberDto
     */
    public void add2Meeting(String meetingId, MeetingMemberDto meetingMemberDto) {
        redisUtils.hset(Constants.REDIS_KEY_MEETING_ROOM + meetingId, meetingMemberDto.getUserId(), meetingMemberDto);
    }

    public List<MeetingMemberDto> getMeetingMemberList(String meetingId) {
        List<MeetingMemberDto> meetingMemberDtoList = redisUtils.hvals(Constants.REDIS_KEY_MEETING_ROOM + meetingId);
        // 只返回正常在会的成员，过滤已退出/被踢/被拉黑的（避免断线重连后显示重复）
        meetingMemberDtoList = meetingMemberDtoList.stream()
                .filter(item -> MeetingMemberStatusEnum.NORMAL.getStatus().equals(item.getStatus()))
                .sorted(Comparator.comparing(MeetingMemberDto::getJoinTime))
                .collect(Collectors.toList());
        return meetingMemberDtoList;
    }

    /**
     * 清理会议室中非 NORMAL 状态的成员（已退出/被踢/被拉黑），
     * 避免断线重连产生新 userId 后旧记录残留。
     */
    public void cleanExitedMembers(String meetingId) {
        List<MeetingMemberDto> all = redisUtils.hvals(Constants.REDIS_KEY_MEETING_ROOM + meetingId);
        List<String> toRemove = all.stream()
                .filter(item -> !MeetingMemberStatusEnum.NORMAL.getStatus().equals(item.getStatus()))
                .map(MeetingMemberDto::getUserId)
                .collect(Collectors.toList());
        if (!toRemove.isEmpty()) {
            redisUtils.hdel(Constants.REDIS_KEY_MEETING_ROOM + meetingId, toRemove.toArray(new String[0]));
        }
    }

    public MeetingMemberDto getMeetingMember(String meetingId, String userId) {
        return (MeetingMemberDto) redisUtils.hget(Constants.REDIS_KEY_MEETING_ROOM + meetingId, userId);
    }

    public Boolean exitMeeting(String meetingId, String userId, MeetingMemberStatusEnum memberStatusEnum) {
        MeetingMemberDto meetingMemberDto = getMeetingMember(meetingId, userId);
        //用户在未正式加入前退出
        if (meetingMemberDto == null) {
            return false;
        }
        meetingMemberDto.setStatus(memberStatusEnum.getStatus());
        add2Meeting(meetingId, meetingMemberDto);
        return true;
    }

    public void removeAllMeetingMember(String meetingId) {
        List<MeetingMemberDto> meetingMemberList = getMeetingMemberList(meetingId);
        List<String> userIdList = meetingMemberList.stream().map(MeetingMemberDto::getUserId).collect(Collectors.toList());
        if (userIdList.isEmpty()) {
            return;
        }
        redisUtils.hdel(Constants.REDIS_KEY_MEETING_ROOM + meetingId, userIdList.toArray(new String[userIdList.size()]));
    }

    /**
     * 从会议室移除指定成员（用于访客重入时清理旧记录）
     */
    public void removeMeetingMember(String meetingId, String userId) {
        redisUtils.hdel(Constants.REDIS_KEY_MEETING_ROOM + meetingId, new String[]{userId});
    }

    public void addInviteInfo(String meetingId, String userId) {
        redisUtils.setex(Constants.REDIS_KEY_INVITE_MEMBER + userId + meetingId, meetingId, Constants.REDIS_KEY_EXPIRES_ONE_MIN * 5);
    }

    public String getInviteInfo(String userId, String meeting) {
        return (String) redisUtils.get(Constants.REDIS_KEY_INVITE_MEMBER + userId + meeting);
    }

    public void saveSysSetting(SysSettingDto sysSettingDto) {
        redisUtils.set(Constants.REDIS_KEY_SYS_SETTING, sysSettingDto);
    }

    public SysSettingDto getSysSetting() {
        SysSettingDto sysSettingDto = (SysSettingDto) redisUtils.get(Constants.REDIS_KEY_SYS_SETTING);
        sysSettingDto = sysSettingDto == null ? new SysSettingDto() : sysSettingDto;
        return sysSettingDto;
    }
}
