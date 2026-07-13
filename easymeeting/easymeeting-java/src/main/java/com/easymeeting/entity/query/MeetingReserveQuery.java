package com.easymeeting.entity.query;

/**
 * 会议预约参数
 */
public class MeetingReserveQuery extends BaseParam {


    /**
     *
     */
    private String meetingId;

    private String meetingIdFuzzy;

    /**
     * 会议主题
     */
    private String meetingName;

    private String meetingNameFuzzy;

    /**
     * 加入类型0:任何人可以加入 1:密码加入 2:联系人加入
     */
    private Integer joinType;

    /**
     * 加入密码
     */
    private String joinPassword;

    private String joinPasswordFuzzy;

    /**
     * 持续时间分钟
     */
    private Integer duration;

    /**
     * 邀请人ID
     */
    private String inviteUserIds;

    private String inviteUserIdsFuzzy;

    /**
     * 开始时间
     */
    private String startTime;

    private String startTimeStart;

    private String startTimeEnd;

    /**
     * 创建时间
     */
    private String createTime;

    private String createTimeStart;

    private String createTimeEnd;

    /**
     * 创建人
     */
    private String createUserId;

    private String createUserIdFuzzy;

    private Integer status;

    private String userId;

    private Boolean queryUserInfo;

    public Boolean getQueryUserInfo() {
        return queryUserInfo;
    }

    public void setQueryUserInfo(Boolean queryUserInfo) {
        this.queryUserInfo = queryUserInfo;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public void setMeetingId(String meetingId) {
        this.meetingId = meetingId;
    }

    public String getMeetingId() {
        return this.meetingId;
    }

    public void setMeetingIdFuzzy(String meetingIdFuzzy) {
        this.meetingIdFuzzy = meetingIdFuzzy;
    }

    public String getMeetingIdFuzzy() {
        return this.meetingIdFuzzy;
    }

    public void setMeetingName(String meetingName) {
        this.meetingName = meetingName;
    }

    public String getMeetingName() {
        return this.meetingName;
    }

    public void setMeetingNameFuzzy(String meetingNameFuzzy) {
        this.meetingNameFuzzy = meetingNameFuzzy;
    }

    public String getMeetingNameFuzzy() {
        return this.meetingNameFuzzy;
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

    public void setJoinPasswordFuzzy(String joinPasswordFuzzy) {
        this.joinPasswordFuzzy = joinPasswordFuzzy;
    }

    public String getJoinPasswordFuzzy() {
        return this.joinPasswordFuzzy;
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

    public void setInviteUserIdsFuzzy(String inviteUserIdsFuzzy) {
        this.inviteUserIdsFuzzy = inviteUserIdsFuzzy;
    }

    public String getInviteUserIdsFuzzy() {
        return this.inviteUserIdsFuzzy;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    public String getStartTime() {
        return this.startTime;
    }

    public void setStartTimeStart(String startTimeStart) {
        this.startTimeStart = startTimeStart;
    }

    public String getStartTimeStart() {
        return this.startTimeStart;
    }

    public void setStartTimeEnd(String startTimeEnd) {
        this.startTimeEnd = startTimeEnd;
    }

    public String getStartTimeEnd() {
        return this.startTimeEnd;
    }

    public void setCreateTime(String createTime) {
        this.createTime = createTime;
    }

    public String getCreateTime() {
        return this.createTime;
    }

    public void setCreateTimeStart(String createTimeStart) {
        this.createTimeStart = createTimeStart;
    }

    public String getCreateTimeStart() {
        return this.createTimeStart;
    }

    public void setCreateTimeEnd(String createTimeEnd) {
        this.createTimeEnd = createTimeEnd;
    }

    public String getCreateTimeEnd() {
        return this.createTimeEnd;
    }

    public void setCreateUserId(String createUserId) {
        this.createUserId = createUserId;
    }

    public String getCreateUserId() {
        return this.createUserId;
    }

    public void setCreateUserIdFuzzy(String createUserIdFuzzy) {
        this.createUserIdFuzzy = createUserIdFuzzy;
    }

    public String getCreateUserIdFuzzy() {
        return this.createUserIdFuzzy;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }
}
