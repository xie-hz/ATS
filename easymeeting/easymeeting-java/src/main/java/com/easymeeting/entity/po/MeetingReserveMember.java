package com.easymeeting.entity.po;

import com.fasterxml.jackson.annotation.JsonIgnore;
import java.io.Serializable;


/**
 * 会议预约成员
 */
public class MeetingReserveMember implements Serializable {


	/**
	 * 会议ID
	 */
	private String meetingId;

	/**
	 * 邀请人ID
	 */
	private String inviteUserId;


	public void setMeetingId(String meetingId){
		this.meetingId = meetingId;
	}

	public String getMeetingId(){
		return this.meetingId;
	}

	public void setInviteUserId(String inviteUserId){
		this.inviteUserId = inviteUserId;
	}

	public String getInviteUserId(){
		return this.inviteUserId;
	}

	@Override
	public String toString (){
		return "会议ID:"+(meetingId == null ? "空" : meetingId)+"，邀请人ID:"+(inviteUserId == null ? "空" : inviteUserId);
	}
}
