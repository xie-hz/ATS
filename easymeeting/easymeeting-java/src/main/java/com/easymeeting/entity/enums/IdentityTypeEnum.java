package com.easymeeting.entity.enums;


public enum IdentityTypeEnum {
    USER(0, "正式用户"),
    GUEST(1, "访客");

    private Integer type;
    private String desc;

    IdentityTypeEnum(Integer type, String desc) {
        this.type = type;
        this.desc = desc;
    }

    public static IdentityTypeEnum getByType(Integer type) {
        for (IdentityTypeEnum item : IdentityTypeEnum.values()) {
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
