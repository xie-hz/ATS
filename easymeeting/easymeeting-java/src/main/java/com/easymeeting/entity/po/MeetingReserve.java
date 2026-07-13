package com.easymeeting.entity.po;

import com.easymeeting.entity.enums.DateTimePatternEnum;
import com.easymeeting.utils.DateUtil;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.util.Date;


/**
 * 会议预约
 */
public class MeetingReserve implements Serializable {


    /**
     *
     */
    private String meetingId;

    /**
     * 会议主题
     */
    private String meetingName;

    /**
     * 加入类型0:任何人可以加入 1:密码加入 2:联系人加入
     */
    private Integer joinType;

    /**
     * 加入密码
     */
    private String joinPassword;

    /**
     * 持续时间分钟
     */
    private Integer duration;

    /**
     * 邀请人ID
     */
    private String inviteUserIds;

    /**
     * 开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm", timezone = "GMT+8")
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm")
    private Date startTime;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;

    /**
     * 创建人
     */
    private String createUserId;


    private String nickName;

    private Integer status;

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public String getNickName() {
        return nickName;
    }

    public void setNickName(String nickName) {
        this.nickName = nickName;
    }

    public void setMeetingId(String meetingId) {
        this.meetingId = meetingId;
    }

    public String getMeetingId() {
        return this.meetingId;
    }

    public void setMeetingName(String meetingName) {
        this.meetingName = meetingName;
    }

    public String getMeetingName() {
        return this.meetingName;
    }

    public void setJoinType(Integer joinType) {
        this.joinType = joinType;
    }

    public Integer getJoinType() {
        return this.joinType;
    }

    public void setJoinPassword(String joinPassword) {
        this.joinPassword = joinPassword;
    }

    public String getJoinPassword() {
        return this.joinPassword;
    }

    public void setDuration(Integer duration) {
        this.duration = duration;
    }

    public Integer getDuration() {
        return this.duration;
    }

    public void setInviteUserIds(String inviteUserIds) {
        this.inviteUserIds = inviteUserIds;
    }

    public String getInviteUserIds() {
        return this.inviteUserIds;
    }

    public void setStartTime(Date startTime) {
        this.startTime = startTime;
    }

    public Date getStartTime() {
        return this.startTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    public Date getCreateTime() {
        return this.createTime;
    }

    public void setCreateUserId(String createUserId) {
        this.createUserId = createUserId;
    }

    public String getCreateUserId() {
        return this.createUserId;
    }

    @Override
    public String toString() {
        return "meetingId:" + (meetingId == null ? "空" : meetingId) + "，会议主题:" + (meetingName == null ? "空" : meetingName) + "，加入类型0:任何人可以加入 1:密码加入 2:联系人加入:" + (joinType == null ? "空" : joinType) + "，加入密码:" + (joinPassword == null ? "空" : joinPassword) + "，持续时间分钟:" + (duration == null ? "空" : duration) + "，邀请人ID:" + (inviteUserIds == null ? "空" : inviteUserIds) + "，开始时间:" + (startTime == null ? "空" : DateUtil.format(
                startTime,
                DateTimePatternEnum.YYYY_MM_DD_HH_MM_SS.getPattern())) + "，创建时间:" + (createTime == null ? "空" : DateUtil.format(createTime,
                DateTimePatternEnum.YYYY_MM_DD_HH_MM_SS.getPattern())) + "，创建人:" + (createUserId == null ? "空" : createUserId);
    }
}
