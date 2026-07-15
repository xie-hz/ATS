package com.easymeeting.service;

import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.MeetingMemberStatusEnum;
import com.easymeeting.entity.po.MeetingInfo;
import com.easymeeting.entity.query.MeetingInfoQuery;
import com.easymeeting.entity.vo.PaginationResultVO;
import io.netty.channel.Channel;

import java.util.List;


/**
 * 业务接口
 */
public interface MeetingInfoService {

    /**
     * 根据条件查询列表
     */
    List<MeetingInfo> findListByParam(MeetingInfoQuery param);

    /**
     * 根据条件查询列表
     */
    Integer findCountByParam(MeetingInfoQuery param);

    /**
     * 分页查询
     */
    PaginationResultVO<MeetingInfo> findListByPage(MeetingInfoQuery param);

    /**
     * 新增
     */
    Integer add(MeetingInfo bean);

    /**
     * 批量新增
     */
    Integer addBatch(List<MeetingInfo> listBean);

    /**
     * 批量新增/修改
     */
    Integer addOrUpdateBatch(List<MeetingInfo> listBean);

    /**
     * 多条件更新
     */
    Integer updateByParam(MeetingInfo bean, MeetingInfoQuery param);

    /**
     * 多条件删除
     */
    Integer deleteByParam(MeetingInfoQuery param);

    /**
     * 根据MeetingId查询对象
     */
    MeetingInfo getMeetingInfoByMeetingId(String meetingId);


    /**
     * 根据MeetingId修改
     */
    Integer updateMeetingInfoByMeetingId(MeetingInfo bean, String meetingId);


    /**
     * 根据MeetingId删除
     */
    Integer deleteMeetingInfoByMeetingId(String meetingId);

    void quickMeeting(MeetingInfo meetingInfo, String nickName);

    String preJoinMeeting(String meetingNo, TokenUserInfoDto tokenUserInfoDto, String password);

    void joinMeeting(String meetingId, String userId, String nickName, Integer sex, Boolean openVideo, Integer identityType);

    /**
     * 访客入会：会议号+密码+昵称，签发临时 GUEST token，返回 token + 会议信息。
     * 不创建 EasyMeeting 账号。
     */
    com.easymeeting.entity.vo.GuestJoinVO guestJoinMeeting(String meetingNo, String password, String nickName, String email);

    /**
     * 开放接口：ATS 服务账号代建面试会议，记录 hostUserId 为创建人/主持人。
     * startTime 为面试预约时间（用于计算 1 小时窗口），null 则用当前时间。
     */
    MeetingInfo createInterviewMeeting(String hostUserId, String meetingName, Integer joinType, String joinPassword, String atsBusinessId, java.util.Date startTime);

    void exitMeetingRoom(TokenUserInfoDto tokenUserInfoDto, MeetingMemberStatusEnum memberStatusEnum);

    void forceExitMeeting(TokenUserInfoDto tokenUserInfoDto, String userId, MeetingMemberStatusEnum memberStatusEnum);

    void removeContext(Channel channel);

    void finishMeeting(String meetingId, String userId);

    void inviteMember(TokenUserInfoDto tokenUserInfoDto, String selectContactIds);

    void acceptInvite(TokenUserInfoDto tokenUserInfoDto,String meetingId);

    void reserveJoinMeeting(String meetingId, TokenUserInfoDto tokenUserInfoDto, String joinPassword);

    void updateMemberOpenVideo(String meetingId, String userId, Boolean openVideo);
}