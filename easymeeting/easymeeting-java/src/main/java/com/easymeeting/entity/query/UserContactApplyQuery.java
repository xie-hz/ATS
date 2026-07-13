package com.easymeeting.entity.query;


/**
 * 联系人申请参数
 */
public class UserContactApplyQuery extends BaseParam {


    /**
     * 自增ID
     */
    private Integer applyId;

    /**
     * 申请人id
     */
    private String applyUserId;

    private String applyUserIdFuzzy;

    /**
     * 接收人ID
     */
    private String receiveUserId;

    private String receiveUserIdFuzzy;

    /**
     * 最后申请时间
     */
    private Long lastApplyTime;

    /**
     * 状态0:待处理 1:已同意  2:已拒绝 3:已拉黑
     */
    private Integer status;

    private Boolean queryUserInfo;

    public Boolean getQueryUserInfo() {
        return queryUserInfo;
    }

    public void setQueryUserInfo(Boolean queryUserInfo) {
        this.queryUserInfo = queryUserInfo;
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

    public void setApplyUserIdFuzzy(String applyUserIdFuzzy) {
        this.applyUserIdFuzzy = applyUserIdFuzzy;
    }

    public String getApplyUserIdFuzzy() {
        return this.applyUserIdFuzzy;
    }

    public void setReceiveUserId(String receiveUserId) {
        this.receiveUserId = receiveUserId;
    }

    public String getReceiveUserId() {
        return this.receiveUserId;
    }

    public void setReceiveUserIdFuzzy(String receiveUserIdFuzzy) {
        this.receiveUserIdFuzzy = receiveUserIdFuzzy;
    }

    public String getReceiveUserIdFuzzy() {
        return this.receiveUserIdFuzzy;
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

}
