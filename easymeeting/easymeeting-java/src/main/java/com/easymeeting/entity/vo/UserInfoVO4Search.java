package com.easymeeting.entity.vo;

public class UserInfoVO4Search {
    /**
     * 用户ID
     */
    private String userId;
    /**
     * 昵称
     */
    private String nickName;

    private Integer status;

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getNickName() {
        return nickName;
    }

    public void setNickName(String nickName) {
        this.nickName = nickName;
    }
}
