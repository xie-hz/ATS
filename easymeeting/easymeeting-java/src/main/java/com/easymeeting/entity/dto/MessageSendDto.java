package com.easymeeting.entity.dto;

import com.alibaba.fastjson.annotation.JSONField;
import com.alibaba.fastjson.serializer.ToStringSerializer;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.io.Serializable;

@JsonIgnoreProperties(ignoreUnknown = true)
public class MessageSendDto<T> implements Serializable {
    private static final long serialVersionUID = -1045752033171142417L;

    private Integer messageSend2Type;

    private String meetingId;

    //消息类型
    private Integer messageType;

    private String sendUserId;

    private String sendUserNickName;

    private T messageContent;

    private String receiveUserId;

    private Long sendTime;

    @JSONField(serializeUsing = ToStringSerializer.class)
    private Long messageId;

    private Integer status;

    private String fileName;

    private Integer fileType;

    private Long fileSize;

    public Integer getMessageSend2Type() {
        return messageSend2Type;
    }

    public void setMessageSend2Type(Integer messageSend2Type) {
        this.messageSend2Type = messageSend2Type;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public Integer getFileType() {
        return fileType;
    }

    public void setFileType(Integer fileType) {
        this.fileType = fileType;
    }

    public Long getFileSize() {
        return fileSize;
    }

    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Long getMessageId() {
        return messageId;
    }

    public void setMessageId(Long messageId) {
        this.messageId = messageId;
    }

    public Long getSendTime() {
        return sendTime;
    }

    public void setSendTime(Long sendTime) {
        this.sendTime = sendTime;
    }

    public String getReceiveUserId() {
        return receiveUserId;
    }

    public void setReceiveUserId(String receiveUserId) {
        this.receiveUserId = receiveUserId;
    }

    public T getMessageContent() {
        return messageContent;
    }

    public void setMessageContent(T messageContent) {
        this.messageContent = messageContent;
    }

    public String getSendUserId() {
        return sendUserId;
    }

    public void setSendUserId(String sendUserId) {
        this.sendUserId = sendUserId;
    }

    public String getSendUserNickName() {
        return sendUserNickName;
    }

    public void setSendUserNickName(String sendUserNickName) {
        this.sendUserNickName = sendUserNickName;
    }

    public Integer getMessageType() {
        return messageType;
    }

    public void setMessageType(Integer messageType) {
        this.messageType = messageType;
    }

    public String getMeetingId() {
        return meetingId;
    }

    public void setMeetingId(String meetingId) {
        this.meetingId = meetingId;
    }
}
