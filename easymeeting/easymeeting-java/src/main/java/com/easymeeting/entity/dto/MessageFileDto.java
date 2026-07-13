package com.easymeeting.entity.dto;

public class MessageFileDto {
    private String fileName;
    private Integer fileType;

    public MessageFileDto() {

    }

    public MessageFileDto(String fileName, Integer fileType) {
        this.fileName = fileName;
        this.fileType = fileType;
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
}
