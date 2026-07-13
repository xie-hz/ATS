package com.easymeeting.entity.po;

import com.easymeeting.entity.enums.UserContactApplyStatusEnum;

import java.io.Serializable;


/**
 * 联系人申请
 */
public class UserContactApply implements Serializable {


    /**
     * 自增ID
     */
    private Integer applyId;

    /**
     * 申请人id
     */
    private String applyUserId;

    /**
     * 接收人ID
     */
    private String receiveUserId;

    /**
     * 最后申请时间
     */
    private Long lastApplyTime;

    /**
     * 状态0:待处理 1:已同意  2:已拒绝 3:已拉黑
     */
    private Integer status;

    private String nickName;

    private String statusName;

    public String getStatusName() {
        UserContactApplyStatusEnum statusEnum = UserContactApplyStatusEnum.getByStatus(status);
        return statusEnum == null ? "" : statusEnum.getDesc();
    }

    public void setStatusName(String statusName) {
        this.statusName = statusName;
    }

    public String getNickName() {
        return nickName;
    }

    public void setNickName(String nickName) {
        this.nickName = nickName;
    }

    public void setApplyId(Integer applyId) {
        this.applyId = applyId;
    }

    public Integer getApplyId() {
        return this.applyId;
    }

    public void setApplyUserId(String applyUserId) {
        this.applyUserId = applyUserId;
    }

    public String getApplyUserId() {
        return this.applyUserId;
    }

    public void setReceiveUserId(String receiveUserId) {
        this.receiveUserId = receiveUserId;
    }

    public String getReceiveUserId() {
        return this.receiveUserId;
    }

    public void setLastApplyTime(Long lastApplyTime) {
        this.lastApplyTime = lastApplyTime;
    }

    public Long getLastApplyTime() {
        return this.lastApplyTime;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Integer getStatus() {
        return this.status;
    }

    @Override
    public String toString() {
        return "自增ID:" + (applyId == null ? "空" : applyId) + "，申请人id:" + (applyUserId == null ? "空" : applyUserId) + "，接收人ID:" + (receiveUserId == null ? "空" : receiveUserId) + "，最后申请时间:" + (lastApplyTime == null ? "空" : lastApplyTime) + "，状态0:待处理 1:已同意  2:已拒绝 3:已拉黑:" + (status == null ? "空" : status);
    }
}
