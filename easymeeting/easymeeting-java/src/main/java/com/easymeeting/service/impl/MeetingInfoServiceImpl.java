package com.easymeeting.service.impl;

import com.easymeeting.entity.dto.*;
import com.easymeeting.entity.enums.*;
import com.easymeeting.entity.po.*;
import com.easymeeting.entity.query.*;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.entity.vo.GuestJoinVO;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.mappers.*;
import com.easymeeting.redis.RedisComponet;
import com.easymeeting.service.AtsWebhookService;
import com.easymeeting.service.MeetingInfoService;
import com.easymeeting.utils.JsonUtils;
import com.easymeeting.utils.StringTools;
import com.easymeeting.websocket.ChannelContextUtils;
import com.easymeeting.websocket.message.MessageHandler;
import io.netty.channel.Channel;
import io.netty.util.Attribute;
import io.netty.util.AttributeKey;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ArrayUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;


/**
 * 业务接口实现
 */
@Service("meetingInfoService")
@Slf4j
public class MeetingInfoServiceImpl implements MeetingInfoService {

    @Resource
    private MeetingInfoMapper<MeetingInfo, MeetingInfoQuery> meetingInfoMapper;

    @Resource
    private RedisComponet redisComponet;

    @Resource
    private ChannelContextUtils channelContextUtils;

    @Resource
    private MeetingMemberMapper<MeetingMember, MeetingMemberQuery> meetingMemberMapper;

    @Resource
    private UserInfoMapper<UserInfo, UserInfoQuery> userInfoMapper;

    @Resource
    private MessageHandler messageHandler;

    @Resource
    private AtsWebhookService atsWebhookService;

    @Resource
    private UserContactMapper<UserContact, UserContactQuery> userContactMapper;

    @Resource
    private MeetingReserveMapper<MeetingReserve, MeetingReserveQuery> meetingReserveMapper;

    @Resource
    private MeetingReserveMemberMapper<MeetingReserveMember, MeetingReserveMemberQuery> meetingReserveMemberMapper;

    /**
     * 根据条件查询列表
     */
    @Override
    public List<MeetingInfo> findListByParam(MeetingInfoQuery param) {
        return this.meetingInfoMapper.selectList(param);
    }

    /**
     * 根据条件查询列表
     */
    @Override
    public Integer findCountByParam(MeetingInfoQuery param) {
        return this.meetingInfoMapper.selectCount(param);
    }

    /**
     * 分页查询方法
     */
    @Override
    public PaginationResultVO<MeetingInfo> findListByPage(MeetingInfoQuery param) {
        int count = this.findCountByParam(param);
        int pageSize = param.getPageSize() == null ? PageSize.SIZE15.getSize() : param.getPageSize();

        SimplePage page = new SimplePage(param.getPageNo(), count, pageSize);
        param.setSimplePage(page);
        List<MeetingInfo> list = this.findListByParam(param);
        PaginationResultVO<MeetingInfo> result = new PaginationResultVO(count, page.getPageSize(), page.getPageNo(), page.getPageTotal(), list);
        return result;
    }

    /**
     * 新增
     */
    @Override
    public Integer add(MeetingInfo bean) {
        return this.meetingInfoMapper.insert(bean);
    }

    /**
     * 批量新增
     */
    @Override
    public Integer addBatch(List<MeetingInfo> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.meetingInfoMapper.insertBatch(listBean);
    }

    /**
     * 批量新增或者修改
     */
    @Override
    public Integer addOrUpdateBatch(List<MeetingInfo> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.meetingInfoMapper.insertOrUpdateBatch(listBean);
    }

    /**
     * 多条件更新
     */
    @Override
    public Integer updateByParam(MeetingInfo bean, MeetingInfoQuery param) {
        StringTools.checkParam(param);
        return this.meetingInfoMapper.updateByParam(bean, param);
    }

    /**
     * 多条件删除
     */
    @Override
    public Integer deleteByParam(MeetingInfoQuery param) {
        StringTools.checkParam(param);
        return this.meetingInfoMapper.deleteByParam(param);
    }

    /**
     * 根据MeetingId获取对象
     */
    @Override
    public MeetingInfo getMeetingInfoByMeetingId(String meetingId) {
        return this.meetingInfoMapper.selectByMeetingId(meetingId);
    }

    /**
     * 根据MeetingId修改
     */
    @Override
    public Integer updateMeetingInfoByMeetingId(MeetingInfo bean, String meetingId) {
        return this.meetingInfoMapper.updateByMeetingId(bean, meetingId);
    }

    /**
     * 根据MeetingId删除
     */
    @Override
    public Integer deleteMeetingInfoByMeetingId(String meetingId) {
        return this.meetingInfoMapper.deleteByMeetingId(meetingId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void quickMeeting(MeetingInfo meetingInfo, String nickName) {
        Date curDate = new Date();
        meetingInfo.setCreateTime(curDate);
        meetingInfo.setMeetingId(StringTools.getMeetingNoOrMeetingId());
        meetingInfo.setStartTime(curDate);
        meetingInfo.setStatus(MeetingStatusEnum.RUNING.getStatus());
        this.meetingInfoMapper.insert(meetingInfo);
    }


    @Override
    public String preJoinMeeting(String meetingNo, TokenUserInfoDto tokenUserInfoDto, String password) {
        String userId = tokenUserInfoDto.getUserId();
        MeetingInfoQuery meetingInfoQuery = new MeetingInfoQuery();
        meetingInfoQuery.setMeetingNo(meetingNo);
        meetingInfoQuery.setStatus(MeetingStatusEnum.RUNING.getStatus());
        meetingInfoQuery.setOrderBy("create_time desc");
        List<MeetingInfo> meetingInfoList = meetingInfoMapper.selectList(meetingInfoQuery);
        if (meetingInfoList.isEmpty()) {
            throw new BusinessException("会议不存在");
        }
        MeetingInfo meetingInfo = meetingInfoList.get(0);
        if (!MeetingStatusEnum.RUNING.getStatus().equals(meetingInfo.getStatus())) {
            throw new BusinessException("会议已结束");
        }
        if (!StringTools.isEmpty(tokenUserInfoDto.getCurrentMeetingId()) && !meetingInfo.getMeetingId().equals(tokenUserInfoDto.getCurrentMeetingId())) {
            // 检查旧会议是否真的还在进行中且用户还在里面
            MeetingMemberDto oldMember = redisComponet.getMeetingMember(tokenUserInfoDto.getCurrentMeetingId(), userId);
            if (oldMember != null && MeetingMemberStatusEnum.NORMAL.getStatus().equals(oldMember.getStatus())) {
                throw new BusinessException("你有未结束的会议无法加入其他会议");
            }
            // 旧会议已不在或已退出，清除残留的 currentMeetingId
            tokenUserInfoDto.setCurrentMeetingId(null);
            redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
        }
        checkMeetingJoin(meetingInfo.getMeetingId(), userId);
        // 会议创建者和管理员免密入会
        boolean isCreator = userId.equals(meetingInfo.getCreateUserId());
        boolean isAdmin = Boolean.TRUE.equals(tokenUserInfoDto.getAdmin());
        if (!isCreator && !isAdmin) {
            if (MeetingJoinTypeEnum.PASSWORD.getType().equals(meetingInfo.getJoinType()) && !meetingInfo.getJoinPassword().equals(password)) {
                throw new BusinessException("入会密码不正确");
            }
        }
        tokenUserInfoDto.setCurrentMeetingId(meetingInfo.getMeetingId());
        redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
        return meetingInfo.getMeetingId();
    }

    private void checkMeetingJoin(String meetingId, String userId) {
        MeetingMemberDto meetingMemberDto = redisComponet.getMeetingMember(meetingId, userId);
        if (meetingMemberDto != null && MeetingMemberStatusEnum.BLACKLIST.getStatus().equals(meetingMemberDto.getStatus())) {
            throw new BusinessException("你已被拉黑无法加入会议");
        }
    }

    //加入成员
    private void addMeetingMember(String meetingId, String userId, String nickName, Integer memberType, Integer identityType) {
        MeetingMember meetingMember = new MeetingMember();
        meetingMember.setMeetingId(meetingId);
        meetingMember.setUserId(userId);
        meetingMember.setNickName(nickName);
        meetingMember.setLastJoinTime(new Date());
        meetingMember.setStatus(MeetingMemberStatusEnum.NORMAL.getStatus());
        meetingMember.setMemberType(memberType);
        meetingMember.setMeetingStatus(MeetingStatusEnum.RUNING.getStatus());
        meetingMember.setIdentityType(identityType == null ? IdentityTypeEnum.USER.getType() : identityType);
        this.meetingMemberMapper.insertOrUpdate(meetingMember);
    }

    //加入会议
    private void add2Meeting(String meetingId, String userId, String nickName, Integer sex, Integer memberType, Boolean openVideo, Integer identityType) {
        MeetingMemberDto meetingMemberDto = new MeetingMemberDto();
        meetingMemberDto.setUserId(userId);
        meetingMemberDto.setNickName(nickName);
        meetingMemberDto.setJoinTime(System.currentTimeMillis());
        meetingMemberDto.setMemberType(memberType);
        meetingMemberDto.setStatus(MeetingMemberStatusEnum.NORMAL.getStatus());
        meetingMemberDto.setOpenVideo(openVideo);
        meetingMemberDto.setSex(sex);
        meetingMemberDto.setIdentityType(identityType == null ? IdentityTypeEnum.USER.getType() : identityType);
        redisComponet.add2Meeting(meetingId, meetingMemberDto);
    }

    @Override
    public void joinMeeting(String meetingId, String userId, String nickName, Integer sex, Boolean openVideo, Integer identityType) {
        if (StringTools.isEmpty(meetingId)) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        MeetingInfo meetingInfo = this.meetingInfoMapper.selectByMeetingId(meetingId);
        if (meetingInfo == null || MeetingStatusEnum.FINISHED.getStatus().equals(meetingInfo.getStatus())) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        this.checkMeetingJoin(meetingId, userId);
        // 清理已退出/被踢的旧成员记录，避免断线重连产生新 userId 后残留重复
        redisComponet.cleanExitedMembers(meetingId);
        MemberTypeEnum memberTypeEnum = meetingInfo.getCreateUserId().equals(userId) ? MemberTypeEnum.COMPERE : MemberTypeEnum.NORMAL;
        this.addMeetingMember(meetingId, userId, nickName, memberTypeEnum.getType(), identityType);
        this.add2Meeting(meetingId, userId, nickName, sex, memberTypeEnum.getType(), openVideo, identityType);

        //加入ws
        channelContextUtils.addMeetingRoom(meetingId, userId);
        //发送ws消息
        MeetingJoinDto meetingJoinDto = new MeetingJoinDto();
        meetingJoinDto.setMeetingMemberList(redisComponet.getMeetingMemberList(meetingId));
        meetingJoinDto.setNewMember(redisComponet.getMeetingMember(meetingId, userId));
        MessageSendDto messageSendDto = new MessageSendDto();
        messageSendDto.setMessageType(MessageTypeEnum.ADD_MEETING_ROOM.getType());
        messageSendDto.setMessageContent(meetingJoinDto);
        messageSendDto.setMeetingId(meetingId);
        messageSendDto.setMessageSend2Type(MessageSend2TypeEnum.GROUP.getType());
        messageHandler.sendMessage(messageSendDto);
    }

    @Override
    public GuestJoinVO guestJoinMeeting(String meetingNo, String password, String nickName, String email) {
        if (StringTools.isEmpty(meetingNo) || StringTools.isEmpty(nickName)) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        MeetingInfoQuery meetingInfoQuery = new MeetingInfoQuery();
        meetingInfoQuery.setMeetingNo(meetingNo.replace(" ", ""));
        meetingInfoQuery.setStatus(MeetingStatusEnum.RUNING.getStatus());
        meetingInfoQuery.setOrderBy("create_time desc");
        List<MeetingInfo> meetingInfoList = meetingInfoMapper.selectList(meetingInfoQuery);
        if (meetingInfoList.isEmpty()) {
            throw new BusinessException("会议不存在");
        }
        MeetingInfo meetingInfo = meetingInfoList.get(0);
        if (!MeetingStatusEnum.RUNING.getStatus().equals(meetingInfo.getStatus())) {
            throw new BusinessException("会议已结束");
        }
        if (MeetingJoinTypeEnum.PASSWORD.getType().equals(meetingInfo.getJoinType())
                && !meetingInfo.getJoinPassword().equals(password)) {
            throw new BusinessException("入会密码不正确");
        }
        // 生成访客身份：如果有邮箱，用邮箱 hash 生成确定性 userId（同一邮箱每次相同，
        // 刷新/重入不会产生重复成员）；没邮箱则用随机数。
        String guestUserId;
        if (!StringTools.isEmpty(email)) {
            // email.hashCode() 可能为负，取绝对值后模 10^10 得到 10 位数字，加 G 前缀 = 11 字符 ≤ varchar(12)
            long hash = Math.abs((long) email.hashCode()) % 10000000000L;
            guestUserId = "G" + String.format("%010d", hash);
        } else {
            guestUserId = "G" + StringTools.getMeetingNoOrMeetingId();
        }
        // 如果该 userId 在会议中已有旧记录（EXIT/被踢等），先清理，防止重复
        redisComponet.cleanExitedMembers(meetingInfo.getMeetingId());
        MeetingMemberDto existing = redisComponet.getMeetingMember(meetingInfo.getMeetingId(), guestUserId);
        if (existing != null) {
            // 已有同 userId 的成员（可能还在会中），从 Redis Hash 删除旧记录
            redisComponet.removeMeetingMember(meetingInfo.getMeetingId(), guestUserId);
        }
        String token = StringTools.getMeetingNoOrMeetingId() + StringTools.getMeetingNoOrMeetingId();
        TokenUserInfoDto tokenUserInfoDto = new TokenUserInfoDto();
        tokenUserInfoDto.setToken(token);
        tokenUserInfoDto.setUserId(guestUserId);
        tokenUserInfoDto.setNickName(nickName);
        tokenUserInfoDto.setCurrentNickName(nickName);
        tokenUserInfoDto.setCurrentMeetingId(meetingInfo.getMeetingId());
        tokenUserInfoDto.setIdentityType(IdentityTypeEnum.GUEST.getType());
        tokenUserInfoDto.setAdmin(false);
        redisComponet.saveGuestTokenUserInfoDto(tokenUserInfoDto);

        GuestJoinVO vo = new GuestJoinVO();
        vo.setToken(token);
        vo.setUserId(guestUserId);
        vo.setMeetingId(meetingInfo.getMeetingId());
        vo.setMeetingNo(meetingInfo.getMeetingNo());
        vo.setMeetingName(meetingInfo.getMeetingName());
        return vo;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public MeetingInfo createInterviewMeeting(String hostUserId, String meetingName, Integer joinType, String joinPassword, String atsBusinessId, java.util.Date startTime) {
        if (StringTools.isEmpty(hostUserId) || StringTools.isEmpty(meetingName)) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        MeetingInfo meetingInfo = new MeetingInfo();
        meetingInfo.setMeetingId(StringTools.getMeetingNoOrMeetingId());
        meetingInfo.setMeetingNo(StringTools.getMeetingNoOrMeetingId());
        meetingInfo.setMeetingName(meetingName);
        meetingInfo.setJoinType(joinType == null ? MeetingJoinTypeEnum.PASSWORD.getType() : joinType);
        meetingInfo.setJoinPassword(joinPassword);
        meetingInfo.setCreateUserId(hostUserId);
        Date curDate = new Date();
        meetingInfo.setCreateTime(curDate);
        meetingInfo.setStartTime(startTime != null ? startTime : curDate);
        meetingInfo.setStatus(MeetingStatusEnum.RUNING.getStatus());
        meetingInfo.setSource(MeetingSourceEnum.ATS_INTERVIEW.getType());
        meetingInfo.setAtsBusinessId(atsBusinessId);
        this.meetingInfoMapper.insert(meetingInfo);
        return meetingInfo;
    }


    /**
     * 用户退出房间
     *
     * @param tokenUserInfoDto
     * @param memberStatusEnum
     */
    @Override
    public void exitMeetingRoom(TokenUserInfoDto tokenUserInfoDto, MeetingMemberStatusEnum memberStatusEnum) {
        String meetingId = tokenUserInfoDto.getCurrentMeetingId();
        if (StringTools.isEmpty(meetingId)) {
            return;
        }
        String userId = tokenUserInfoDto.getUserId();
        Boolean exit = redisComponet.exitMeeting(meetingId, userId, memberStatusEnum);
        if (!exit) {
            tokenUserInfoDto.setCurrentMeetingId(null);
            redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
            return;
        }
        //通知其他人
        MessageSendDto messageSendDto = new MessageSendDto();
        messageSendDto.setMessageType(MessageTypeEnum.EXIT_MEETING_ROOM.getType());

        //清空当前正在进行的会议
        tokenUserInfoDto.setCurrentMeetingId(null);
        redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);

        List<MeetingMemberDto> meetingMemberDtoList = redisComponet.getMeetingMemberList(meetingId);
        MeetingExitDto exitDto = new MeetingExitDto();
        exitDto.setMeetingMemberList(meetingMemberDtoList);
        exitDto.setExitUserId(userId);
        exitDto.setExitStatus(memberStatusEnum.getStatus());
        messageSendDto.setMessageContent(JsonUtils.convertObj2Json(exitDto));
        messageSendDto.setMeetingId(meetingId);
        messageSendDto.setMessageSend2Type(MessageSend2TypeEnum.GROUP.getType());
        messageHandler.sendMessage(messageSendDto);
        //不能再这里操作移除channel，发送消息是消息队列，异步执行，可能在消息发送前已经移除channle,导致收不到消息

        //没有在线用户了，就结束会议
        List<MeetingMemberDto> onlineMemberList =
                meetingMemberDtoList.stream().filter(item -> MeetingMemberStatusEnum.NORMAL.getStatus().equals(item.getStatus())).collect(Collectors.toList());
        if (onlineMemberList.isEmpty()) {
            // ATS 面试会议：默认 1 小时窗口。窗口内（startTime + 1h > now）保留可重入；
            // 窗口外且无人则自动结束。有人时不会进到这个分支（onlineMemberList 非空）。
            MeetingInfo currentMeeting = this.meetingInfoMapper.selectByMeetingId(meetingId);
            if (currentMeeting != null && MeetingSourceEnum.ATS_INTERVIEW.getType().equals(currentMeeting.getSource())) {
                long durationMs = 60 * 60 * 1000; // 默认 1 小时
                if (currentMeeting.getStartTime() != null &&
                        System.currentTimeMillis() > currentMeeting.getStartTime().getTime() + durationMs) {
                    finishMeeting(meetingId, null);
                    return;
                }
                // 未超时，保留会议运行
            } else {
                MeetingReserve meetingReserve = this.meetingReserveMapper.selectByMeetingId(meetingId);
                if (meetingReserve == null) {
                    finishMeeting(meetingId, null);
                    return;
                }
                if (System.currentTimeMillis() > meetingReserve.getStartTime().getTime() + meetingReserve.getDuration() * 60 * 1000) {
                    finishMeeting(meetingId, null);
                    return;
                }
            }
        }
        //更新状态
        if (ArrayUtils.contains(new Integer[]{MeetingMemberStatusEnum.KICK_OUT.getStatus(), MeetingMemberStatusEnum.BLACKLIST.getStatus()},
                memberStatusEnum.getStatus())) {
            MeetingMember meetingMember = new MeetingMember();
            meetingMember.setStatus(memberStatusEnum.getStatus());
            meetingMemberMapper.updateByMeetingIdAndUserId(meetingMember, meetingId, userId);
        }
    }

    /**
     * 强制退出房间
     *
     * @param tokenUserInfoDto
     * @param userId
     * @param memberStatusEnum
     */
    @Override
    public void forceExitMeeting(TokenUserInfoDto tokenUserInfoDto, String userId, MeetingMemberStatusEnum memberStatusEnum) {
        MeetingInfo meetingInfo = this.meetingInfoMapper.selectByMeetingId(tokenUserInfoDto.getCurrentMeetingId());
        if (!meetingInfo.getCreateUserId().equals(tokenUserInfoDto.getUserId())) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        TokenUserInfoDto userInfoDto = this.redisComponet.getTokenUserInfoDtoByUserId(userId);
        exitMeetingRoom(userInfoDto, memberStatusEnum);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void finishMeeting(String meetingId, String userId) {
        MeetingInfo meetingInfo = this.meetingInfoMapper.selectByMeetingId(meetingId);
        if (userId != null && !meetingInfo.getCreateUserId().equals(userId)) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        //更新会议状态为结束
        MeetingInfo updateInfo = new MeetingInfo();
        updateInfo.setStatus(MeetingStatusEnum.FINISHED.getStatus());
        updateInfo.setEndTime(new Date());
        meetingInfoMapper.updateByMeetingId(updateInfo, meetingId);

        // 通知 ATS 会议结束（仅 ATS 面试会议会真正回调）
        meetingInfo.setStatus(MeetingStatusEnum.FINISHED.getStatus());
        atsWebhookService.notifyMeetingEvent(meetingInfo, "FINISHED");

        //发送结束会议消息
        MessageSendDto messageSendDto = new MessageSendDto();
        messageSendDto.setMessageType(MessageTypeEnum.FINIS_MEETING.getType());
        messageSendDto.setMeetingId(meetingId);
        messageSendDto.setMessageSend2Type(MessageSend2TypeEnum.GROUP.getType());
        messageHandler.sendMessage(messageSendDto);

        //更新成员
        MeetingMember meetingMember = new MeetingMember();
        meetingMember.setMeetingStatus(MeetingStatusEnum.FINISHED.getStatus());
        MeetingMemberQuery meetingMemberQuery = new MeetingMemberQuery();
        meetingMemberQuery.setMeetingId(meetingId);
        meetingMemberMapper.updateByParam(meetingMember, meetingMemberQuery);

        //更新预约会议状态
        MeetingReserve updateMeetingReserve = new MeetingReserve();
        updateMeetingReserve.setMeetingId(meetingId);
        updateMeetingReserve.setStatus(MeetingReserveStatusEnum.FINISHED.getStatus());
        meetingReserveMapper.updateByMeetingId(updateMeetingReserve, meetingId);

        List<MeetingMemberDto> meetingMemberDtoList = redisComponet.getMeetingMemberList(meetingId);
        for (MeetingMemberDto meetingMemberDto : meetingMemberDtoList) {
            TokenUserInfoDto userInfoDto = this.redisComponet.getTokenUserInfoDtoByUserId(meetingMemberDto.getUserId());
            if (userInfoDto == null) {
                continue;
            }
            userInfoDto.setCurrentMeetingId(null);
            redisComponet.saveTokenUserInfoDto(userInfoDto);
        }
        //清除列表
        redisComponet.removeAllMeetingMember(meetingId);
    }

    /**
     * 连接断开
     *
     * @param channel
     */
    @Override
    public void removeContext(Channel channel) {
        Attribute<String> attribute = channel.attr(AttributeKey.valueOf(channel.id().toString()));
        String userId = attribute.get();
        if (userId == null) {
            return;
        }
        // 关键修复：检查当前 channel 是否还是 USER_CONTEXT_MAP 中的那个。
        // 如果用户已刷新/重连，新 channel 已替换旧 channel，此时旧 channel 的超时清理
        // 不应删除 token 或退出会议，否则会把新连接也踢掉。
        Channel currentChannel = ChannelContextUtils.USER_CONTEXT_MAP.get(userId);
        if (currentChannel != null && !currentChannel.id().equals(channel.id())) {
            // 旧连接被新连接替换了，只清理心跳，不动 token 和会议状态
            log.info("用户{}的旧连接超时，但新连接已建立，跳过 token 清理和退出会议", userId);
            redisComponet.removeUserHeartBeat(userId);
            return;
        }
        if (!StringTools.isEmpty(userId)) {
            channelContextUtils.removeContextUser(userId);
        }
        redisComponet.removeUserHeartBeat(userId);
        //更新用户最后断线时间
        UserInfo userInfo = new UserInfo();
        userInfo.setLastOffTime(System.currentTimeMillis());
        userInfoMapper.updateByUserId(userInfo, userId);
        TokenUserInfoDto tokenUserInfoDto = redisComponet.getTokenUserInfoDtoByUserId(userId);
        if (tokenUserInfoDto == null) {
            return;
        }
        //优化  将用户信息存储到临时缓存，使劲按1分钟，保证重连后可以获取到
        redisComponet.saveTokenUserInfoDtoTemp(tokenUserInfoDto);

        exitMeetingRoom(tokenUserInfoDto, MeetingMemberStatusEnum.EXIT_MEETING);
        redisComponet.cleanUserTokenByUserId(tokenUserInfoDto.getUserId());

    }

    @Override
    public void inviteMember(TokenUserInfoDto tokenUserInfoDto, String selectContactIds) {
        String[] contactIds = selectContactIds.split(",");
        UserContactQuery contactQuery = new UserContactQuery();
        contactQuery.setUserId(tokenUserInfoDto.getUserId());
        contactQuery.setStatus(UserContactStatusEnum.FRIEND.getStatus());
        List<UserContact> userContacts = userContactMapper.selectList(contactQuery);
        List<String> contactIdList = userContacts.stream().map(item -> item.getContactId()).collect(Collectors.toList());
        if (!contactIdList.containsAll(Arrays.asList(contactIds))) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }

        MeetingInfo meetingInfo = meetingInfoMapper.selectByMeetingId(tokenUserInfoDto.getCurrentMeetingId());

        for (String contactId : contactIds) {
            //判断是否已经加入
            MeetingMemberDto meetingMemberDto = redisComponet.getMeetingMember(tokenUserInfoDto.getCurrentMeetingId(), contactId);
            if (meetingMemberDto != null && MeetingMemberStatusEnum.NORMAL.getStatus().equals(meetingMemberDto.getStatus())) {
                continue;
            }
            redisComponet.addInviteInfo(tokenUserInfoDto.getCurrentMeetingId(), contactId);
            //发送邀请消息
            MessageSendDto messageSendDto = new MessageSendDto();
            messageSendDto.setMessageType(MessageTypeEnum.INVITE_MEMBER_MEETING.getType());
            messageSendDto.setMessageSend2Type(MessageSend2TypeEnum.USER.getType());
            messageSendDto.setReceiveUserId(contactId);

            MeetingInviteDto meetingInviteDto = new MeetingInviteDto();
            meetingInviteDto.setMeetingName(meetingInfo.getMeetingName());
            meetingInviteDto.setInviteUserName(tokenUserInfoDto.getNickName());
            meetingInviteDto.setMeetingId(tokenUserInfoDto.getCurrentMeetingId());
            messageSendDto.setMessageContent(JsonUtils.convertObj2Json(meetingInviteDto));
            messageHandler.sendMessage(messageSendDto);
        }
    }

    @Override
    public void acceptInvite(TokenUserInfoDto tokenUserInfoDto, String meetingId) {
        String redisMeetingId = redisComponet.getInviteInfo(tokenUserInfoDto.getUserId(), meetingId);
        if (null == redisMeetingId) {
            throw new BusinessException("邀请信息已过期");
        }
        tokenUserInfoDto.setCurrentMeetingId(meetingId);
        tokenUserInfoDto.setCurrentNickName(tokenUserInfoDto.getNickName());
        redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
    }

    @Override
    public void reserveJoinMeeting(String meetingId, TokenUserInfoDto tokenUserInfoDto, String joinPassword) {
        String userId = tokenUserInfoDto.getUserId();
        if (!StringTools.isEmpty(tokenUserInfoDto.getCurrentMeetingId()) && !meetingId.equals(tokenUserInfoDto.getCurrentMeetingId())) {
            throw new BusinessException("你有未结束的会议无法加入其他会议");
        }
        checkMeetingJoin(meetingId, userId);

        MeetingReserve meetingReserve = this.meetingReserveMapper.selectByMeetingId(meetingId);
        if (meetingReserve == null) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }

        MeetingReserveMember member = this.meetingReserveMemberMapper.selectByMeetingIdAndInviteUserId(meetingId, tokenUserInfoDto.getUserId());
        if (member == null) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        if (MeetingJoinTypeEnum.PASSWORD.getType().equals(meetingReserve.getJoinType()) && !meetingReserve.getJoinPassword().equals(joinPassword)) {
            throw new BusinessException("入会密码不正确");
        }

        MeetingInfo meetingInfo = this.meetingInfoMapper.selectByMeetingId(meetingId);
        if (meetingInfo == null) {
            meetingInfo = new MeetingInfo();
            meetingInfo.setMeetingName(meetingReserve.getMeetingName());
            meetingInfo.setMeetingNo(meetingReserve.getMeetingId());
            meetingInfo.setJoinType(meetingReserve.getJoinType());
            meetingInfo.setJoinPassword(meetingReserve.getJoinPassword());
            meetingInfo.setCreateUserId(meetingReserve.getCreateUserId());
            Date curDate = new Date();
            meetingInfo.setCreateTime(curDate);
            meetingInfo.setMeetingId(meetingId);
            meetingInfo.setStartTime(curDate);
            meetingInfo.setStatus(MeetingStatusEnum.RUNING.getStatus());
            this.meetingInfoMapper.insert(meetingInfo);
        }
        tokenUserInfoDto.setCurrentMeetingId(meetingId);
        redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
    }

    @Override
    public void updateMemberOpenVideo(String meetingId, String userId, Boolean openVideo) {
        //更新成员状态
        MeetingMemberDto meetingMemberDto = redisComponet.getMeetingMember(meetingId, userId);
        if (meetingMemberDto == null) {
            // 成员尚未正式加入（或已退出），忽略视频状态变更，避免 NPE
            return;
        }
        meetingMemberDto.setOpenVideo(openVideo);
        this.redisComponet.add2Meeting(meetingId, meetingMemberDto);

        MessageSendDto messageSendDto = new MessageSendDto();
        messageSendDto.setMessageType(MessageTypeEnum.MEETING_USER_VIDEO_CHANGE.getType());
        messageSendDto.setMessageContent(openVideo);
        messageSendDto.setSendUserId(userId);
        messageSendDto.setMessageSend2Type(MessageSend2TypeEnum.GROUP.getType());
        messageSendDto.setMeetingId(meetingId);
        messageHandler.sendMessage(messageSendDto);
    }
}