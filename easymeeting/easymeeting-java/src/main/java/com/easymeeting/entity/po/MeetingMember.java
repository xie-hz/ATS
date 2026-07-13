package com.easymeeting.entity.po;

import com.fasterxml.jackson.annotation.JsonIgnore;
import java.util.Date;
import com.easymeeting.entity.enums.DateTimePatternEnum;
import com.easymeeting.utils.DateUtil;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;


/**
 * 参会人员
 */
public class MeetingMember implements Serializable {


	/**
	 * 会议ID
	 */
	private String meetingId;

	/**
	 * 用户ID
	 */
	private String userId;

	/**
	 * 昵称
	 */
	private String nickName;

	/**
	 * 最后入会时间
	 */
	@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
	@DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
	private Date lastJoinTime;

	/**
	 * 1:正常 0:已删除 -1被踢出会议
	 */
	private Integer status;

	/**
	 * 0:普通成员 1:主持人
	 */
	private Integer memberType;

	/**
	 * 状态 0:已结束 1:进行中
	 */
	private Integer meetingStatus;

	/**
	 * 身份类型 0:正式用户(USER) 1:访客(GUEST)
	 */
	private Integer identityType;


	public void setMeetingId(String meetingId){
		this.meetingId = meetingId;
	}

	public String getMeetingId(){
		return this.meetingId;
	}

	public void setUserId(String userId){
		this.userId = userId;
	}

	public String getUserId(){
		return this.userId;
	}

	public void setNickName(String nickName){
		this.nickName = nickName;
	}

	public String getNickName(){
		return this.nickName;
	}

	public void setLastJoinTime(Date lastJoinTime){
		this.lastJoinTime = lastJoinTime;
	}

	public Date getLastJoinTime(){
		return this.lastJoinTime;
	}

	public void setStatus(Integer status){
		this.status = status;
	}

	public Integer getStatus(){
		return this.status;
	}

	public void setMemberType(Integer memberType){
		this.memberType = memberType;
	}

	public Integer getMemberType(){
		return this.memberType;
	}

	public void setMeetingStatus(Integer meetingStatus){
		this.meetingStatus = meetingStatus;
	}

	public Integer getMeetingStatus(){
		return this.meetingStatus;
	}

	public void setIdentityType(Integer identityType){
		this.identityType = identityType;
	}

	public Integer getIdentityType(){
		return this.identityType;
	}

	@Override
	public String toString (){
		return "会议ID:"+(meetingId == null ? "空" : meetingId)+"，用户ID:"+(userId == null ? "空" : userId)+"，昵称:"+(nickName == null ? "空" : nickName)+"，最后入会时间:"+(lastJoinTime == null ? "空" : DateUtil.format(lastJoinTime, DateTimePatternEnum.YYYY_MM_DD_HH_MM_SS.getPattern()))+"，1:正常 0:已删除 -1被踢出会议:"+(status == null ? "空" : status)+"，0:普通成员 1:主持人:"+(memberType == null ? "空" : memberType)+"，状态 0:已结束 1:进行中:"+(meetingStatus == null ? "空" : meetingStatus);
	}
}
