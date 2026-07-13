package com.easymeeting.entity.po;

import com.easymeeting.entity.enums.DateTimePatternEnum;
import com.easymeeting.utils.DateUtil;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.util.Date;


/**
 * 会议信息
 */
public class MeetingInfo implements Serializable {


    /**
     * 会议ID
     */
    private String meetingId;

    /**
     * 会议号
     */
    private String meetingNo;

    /**
     * 会议主题
     */
    private String meetingName;

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

    /**
     * 加入类型0:任何人可以加入 1:密码加入 2:联系人加入
     */
    private Integer joinType;

    /**
     * 加入密码
     */
    private String joinPassword;

    /**
     * 开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date startTime;

    /**
     * 结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date endTime;

    /**
     * 状态0:进行中 1:已结束
     */
    private Integer status;

    /**
     * 会议来源 0:普通会议 1:ATS面试会议
     */
    private Integer source;

    /**
     * ATS业务关联ID（如 ATS 的 interview_id），仅 source=1 时有值
     */
    private String atsBusinessId;

    private Integer memberCount;

    public Integer getMemberCount() {
        return memberCount;
    }

    public void setMemberCount(Integer memberCount) {
        this.memberCount = memberCount;
    }

    public void setMeetingId(String meetingId) {
        this.meetingId = meetingId;
    }

    public String getMeetingId() {
        return this.meetingId;
    }

    public void setMeetingNo(String meetingNo) {
        this.meetingNo = meetingNo;
    }

    public String getMeetingNo() {
        return this.meetingNo;
    }

    public void setMeetingName(String meetingName) {
        this.meetingName = meetingName;
    }

    public String getMeetingName() {
        return this.meetingName;
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

    public void setStartTime(Date startTime) {
        this.startTime = startTime;
    }

    public Date getStartTime() {
        return this.startTime;
    }

    public void setEndTime(Date endTime) {
        this.endTime = endTime;
    }

    public Date getEndTime() {
        return this.endTime;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Integer getStatus() {
        return this.status;
    }

    public void setSource(Integer source) {
        this.source = source;
    }

    public Integer getSource() {
        return this.source;
    }

    public void setAtsBusinessId(String atsBusinessId) {
        this.atsBusinessId = atsBusinessId;
    }

    public String getAtsBusinessId() {
        return this.atsBusinessId;
    }

    @Override
    public String toString() {
        return "会议ID:" + (meetingId == null ? "空" : meetingId) + "，会议号:" + (meetingNo == null ? "空" : meetingNo) + "，会议主题:" + (meetingName == null ? "空" : meetingName) + "，创建时间:" + (createTime == null ? "空" : DateUtil.format(
                createTime,
                DateTimePatternEnum.YYYY_MM_DD_HH_MM_SS.getPattern())) + "，创建人:" + (createUserId == null ? "空" : createUserId) + "，加入类型0:任何人可以加入 1:密码加入 2:联系人加入:" + (joinType == null ? "空" :
                joinType) + "，加入密码:" + (joinPassword == null ? "空" : joinPassword) + "，开始时间:" + (startTime == null ? "空" : DateUtil.format(
                startTime,
                DateTimePatternEnum.YYYY_MM_DD_HH_MM_SS.getPattern())) + "，结束时间:" + (endTime == null ? "空" : DateUtil.format(endTime,
                DateTimePatternEnum.YYYY_MM_DD_HH_MM_SS.getPattern())) + "，状态0:进行中 1:已结束:" + (status == null ? "空" : status);
    }
}
