package com.easymeeting.entity.enums;


public enum ReceiveTypeEnum {
    ALL(0, "全员"),
    USER(1, "个人");

    private Integer type;

    private String msg;

    public static ReceiveTypeEnum getByType(Integer type) {
        for (ReceiveTypeEnum item : ReceiveTypeEnum.values()) {
            if (item.getType().equals(type)) {
                return item;
            }
        }
        return null;
    }

    ReceiveTypeEnum(Integer type, String msg) {
        this.type = type;
        this.msg = msg;
    }

    public Integer getType() {
        return type;
    }

    public String getMsg() {
        return msg;
    }
}
