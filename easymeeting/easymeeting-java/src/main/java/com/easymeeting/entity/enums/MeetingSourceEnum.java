package com.easymeeting.entity.enums;


public enum MeetingSourceEnum {
    NORMAL(0, "普通会议"),
    ATS_INTERVIEW(1, "ATS面试会议");

    private Integer type;
    private String desc;

    MeetingSourceEnum(Integer type, String desc) {
        this.type = type;
        this.desc = desc;
    }

    public static MeetingSourceEnum getByType(Integer type) {
        for (MeetingSourceEnum item : MeetingSourceEnum.values()) {
            if (item.getType().equals(type)) {
                return item;
            }
        }
        return null;
    }

    public Integer getType() {
        return type;
    }

    public String getDesc() {
        return desc;
    }
}
