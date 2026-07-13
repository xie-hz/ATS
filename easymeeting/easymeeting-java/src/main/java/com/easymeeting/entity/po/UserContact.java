package com.easymeeting.entity.po;

import com.easymeeting.entity.constants.Constants;
import com.easymeeting.entity.enums.DateTimePatternEnum;
import com.easymeeting.utils.DateUtil;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.util.Date;


/**
 * 联系人
 */
public class UserContact implements Serializable {


    /**
     * 用户ID
     */
    private String userId;

    /**
     * 联系人ID
     */
    private String contactId;

    /**
     * 状态 0:待处理 1:好友 2:已删除好友 3:已拉黑好友
     */
    private Integer status;

    /**
     * 最后更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date lastUpdateTime;

    private String nickName;

    /**
     * 最后登录时间
     */
    private Long lastLoginTime;

    /**
     * 最后离开时间
     */
    private Long lastOffTime;

    private Integer onlineType;

    public Integer getOnlineType() {
        if (lastLoginTime != null && lastLoginTime > lastOffTime) {
            return Constants.ONE;
        } else {
            return Constants.ZERO;
        }
    }

    public void setOnlineType(Integer onlineType) {
        this.onlineType = onlineType;
    }


    public String getNickName() {
        return nickName;
    }

    public void setNickName(String nickName) {
        this.nickName = nickName;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getUserId() {
        return this.userId;
    }

    public void setContactId(String contactId) {
        this.contactId = contactId;
    }

    public String getContactId() {
        return this.contactId;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Integer getStatus() {
        return this.status;
    }

    public void setLastUpdateTime(Date lastUpdateTime) {
        this.lastUpdateTime = lastUpdateTime;
    }

    public Date getLastUpdateTime() {
        return this.lastUpdateTime;
    }

    @Override
    public String toString() {
        return "用户ID:" + (userId == null ? "空" : userId) + "，联系人ID:" + (contactId == null ? "空" : contactId) + "，状态 0:待处理 1:好友 2:已删除好友 3:已拉黑好友:" + (status == null ? "空" : status) + "，最后更新时间:" + (lastUpdateTime == null ? "空" : DateUtil.format(
                lastUpdateTime,
                DateTimePatternEnum.YYYY_MM_DD_HH_MM_SS.getPattern()));
    }
}
