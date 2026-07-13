package com.easymeeting.entity.enums;


public enum MeetingStatusEnum {
    RUNING(0, "会议进行中"),
    FINISHED(1, "会议已结束");


    private Integer status;
    private String desc;

    MeetingStatusEnum(Integer status, String desc) {
        this.status = status;
        this.desc = desc;
    }


    public static MeetingStatusEnum getByStatus(Integer status) {
        for (MeetingStatusEnum item : MeetingStatusEnum.values()) {
            if (item.getStatus().equals(status)) {
                return item;
            }
        }
        return null;
    }

    public Integer getStatus() {
        return status;
    }

    public String getDesc() {
        return desc;
    }
}
