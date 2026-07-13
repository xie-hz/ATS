package com.easymeeting.entity.query;



/**
 * 会议预约成员参数
 */
public class MeetingReserveMemberQuery extends BaseParam {


	/**
	 * 会议ID
	 */
	private String meetingId;

	private String meetingIdFuzzy;

	/**
	 * 邀请人ID
	 */
	private String inviteUserId;

	private String inviteUserIdFuzzy;


	public void setMeetingId(String meetingId){
		this.meetingId = meetingId;
	}

	public String getMeetingId(){
		return this.meetingId;
	}

	public void setMeetingIdFuzzy(String meetingIdFuzzy){
		this.meetingIdFuzzy = meetingIdFuzzy;
	}

	public String getMeetingIdFuzzy(){
		return this.meetingIdFuzzy;
	}

	public void setInviteUserId(String inviteUserId){
		this.inviteUserId = inviteUserId;
	}

	public String getInviteUserId(){
		return this.inviteUserId;
	}

	public void setInviteUserIdFuzzy(String inviteUserIdFuzzy){
		this.inviteUserIdFuzzy = inviteUserIdFuzzy;
	}

	public String getInviteUserIdFuzzy(){
		return this.inviteUserIdFuzzy;
	}

}
