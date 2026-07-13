package com.easymeeting.controller;

import com.easymeeting.annotation.GlobalInterceptor;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.MeetingMemberStatusEnum;
import com.easymeeting.entity.enums.MeetingStatusEnum;
import com.easymeeting.entity.enums.ResponseCodeEnum;
import com.easymeeting.entity.po.MeetingInfo;
import com.easymeeting.entity.po.MeetingMember;
import com.easymeeting.entity.query.MeetingInfoQuery;
import com.easymeeting.entity.query.MeetingMemberQuery;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.service.MeetingInfoService;
import com.easymeeting.service.MeetingMemberService;
import com.easymeeting.utils.StringTools;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import java.util.List;
import java.util.Optional;

@Validated
@RestController
@RequestMapping("/meeting")
public class MeetingInfoController extends ABaseController {

    @Resource
    private MeetingInfoService meetingInfoService;

    @Resource
    private MeetingMemberService meetingMemberService;

    @RequestMapping("/loadMeeting")
    @GlobalInterceptor
    public ResponseVO loadMeeting(Integer pageNo) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        MeetingInfoQuery infoQuery = new MeetingInfoQuery();
        infoQuery.setUserId(tokenUserInfoDto.getUserId());
        infoQuery.setPageNo(pageNo);
        infoQuery.setOrderBy("m.create_time desc");
        infoQuery.setQueryMemberCount(true);
        PaginationResultVO resultVO = this.meetingInfoService.findListByPage(infoQuery);
        return getSuccessResponseVO(resultVO);
    }

    @RequestMapping("/quickMeeting")
    @GlobalInterceptor
    public ResponseVO quickMeeting(@NotNull Integer meetingNoType, @NotEmpty @Size(max = 100) String meetingName, @NotNull Integer joinType,
                                   @Size(max = 5) String joinPassword) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        if (tokenUserInfoDto.getCurrentMeetingId() != null) {
            throw new BusinessException("你有未结束的会议，无法创建新的会议");
        }
        MeetingInfo meetingInfo = new MeetingInfo();
        meetingInfo.setMeetingName(meetingName);
        meetingInfo.setMeetingNo(meetingNoType == 0 ? tokenUserInfoDto.getMyMeetingNo() : StringTools.getMeetingNoOrMeetingId());
        meetingInfo.setJoinType(joinType);
        meetingInfo.setJoinPassword(joinPassword);
        meetingInfo.setCreateUserId(tokenUserInfoDto.getUserId());
        meetingInfoService.quickMeeting(meetingInfo, tokenUserInfoDto.getNickName());
        tokenUserInfoDto.setCurrentMeetingId(meetingInfo.getMeetingId());
        tokenUserInfoDto.setCurrentNickName(tokenUserInfoDto.getNickName());
        resetTokenUserInfo(tokenUserInfoDto);
        return getSuccessResponseVO(meetingInfo.getMeetingId());
    }

    @RequestMapping("/preJoinMeeting")
    @GlobalInterceptor
    public ResponseVO preJoinMeeting(@NotEmpty String meetingNo, @NotEmpty String nickName, String password) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingNo = meetingNo.replace(" ", "");
        tokenUserInfoDto.setCurrentNickName(nickName);
        String meetingId = meetingInfoService.preJoinMeeting(meetingNo, tokenUserInfoDto, password);
        return getSuccessResponseVO(meetingId);
    }

    @RequestMapping("/joinMeeting")
    @GlobalInterceptor
    public ResponseVO joinMeeting(@NotNull Boolean videoOpen) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingInfoService.joinMeeting(tokenUserInfoDto.getCurrentMeetingId(), tokenUserInfoDto.getUserId(), tokenUserInfoDto.getCurrentNickName(),
                tokenUserInfoDto.getSex(), videoOpen, tokenUserInfoDto.getIdentityType());
        return getSuccessResponseVO(null);
    }

    /**
     * 访客入会（免登录）：会议号 + 密码 + 昵称 -> 签发临时 GUEST token。
     * 供 Web 端候选人与面试官无账号入会使用。
     */
    @RequestMapping("/guestJoin")
    public ResponseVO guestJoin(@NotEmpty String meetingNo, @NotEmpty @Size(max = 50) String nickName, String password) {
        com.easymeeting.entity.vo.GuestJoinVO vo = meetingInfoService.guestJoinMeeting(meetingNo, password, nickName);
        return getSuccessResponseVO(vo);
    }

    @RequestMapping("/exitMeeting")
    @GlobalInterceptor
    public ResponseVO exitMeeting() {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingInfoService.exitMeetingRoom(tokenUserInfoDto, MeetingMemberStatusEnum.EXIT_MEETING);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/kickOutMeeting")
    @GlobalInterceptor
    public ResponseVO kickOutMeeting(@NotEmpty String userId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingInfoService.forceExitMeeting(tokenUserInfoDto, userId, MeetingMemberStatusEnum.KICK_OUT);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/blackMeeting")
    @GlobalInterceptor
    public ResponseVO blackMeeting(@NotEmpty String userId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingInfoService.forceExitMeeting(tokenUserInfoDto, userId, MeetingMemberStatusEnum.BLACKLIST);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/getCurrentMeeting")
    @GlobalInterceptor
    public ResponseVO getCurrentMeeting() {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        if (StringTools.isEmpty(tokenUserInfoDto.getCurrentMeetingId())) {
            return getSuccessResponseVO(null);
        }
        MeetingInfo meetingInfo = this.meetingInfoService.getMeetingInfoByMeetingId(tokenUserInfoDto.getCurrentMeetingId());
        if (MeetingStatusEnum.FINISHED.getStatus().equals(meetingInfo.getStatus())) {
            return getSuccessResponseVO(null);
        }
        return getSuccessResponseVO(meetingInfo);
    }


    @RequestMapping("/finishMeeting")
    @GlobalInterceptor
    public ResponseVO finishMeeting(@NotEmpty String meetingId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        this.meetingInfoService.finishMeeting(meetingId, tokenUserInfoDto.getUserId());
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/delMeetingRecord")
    @GlobalInterceptor
    public ResponseVO delMeetingRecord(@NotEmpty String meetingId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        MeetingMember meetingMember = new MeetingMember();
        meetingMember.setStatus(MeetingMemberStatusEnum.DEL_MEETING.getStatus());
        MeetingMemberQuery meetingMemberQuery = new MeetingMemberQuery();
        meetingMemberQuery.setMeetingId(meetingId);
        meetingMemberQuery.setUserId(tokenUserInfoDto.getUserId());
        meetingMemberService.updateByParam(meetingMember, meetingMemberQuery);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/loadMeetingMembers")
    @GlobalInterceptor
    public ResponseVO loadMeetingMembers(@NotEmpty String meetingId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        MeetingMemberQuery meetingMemberQuery = new MeetingMemberQuery();
        meetingMemberQuery.setMeetingId(meetingId);
        List<MeetingMember> meetingMemberList = this.meetingMemberService.findListByParam(meetingMemberQuery);
        Optional<MeetingMember> first = meetingMemberList.stream().filter(item -> item.getUserId().equals(tokenUserInfoDto.getUserId())).findFirst(); // 9
        if (!first.isPresent()) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        return getSuccessResponseVO(meetingMemberList);
    }

    /**
     * 预约入会
     *
     * @param meetingId
     * @param nickName
     * @param joinPassword
     * @return
     */
    @RequestMapping("/reserveJoinMeeting")
    @GlobalInterceptor
    public ResponseVO reserveJoinMeeting(@NotEmpty String meetingId, @NotEmpty String nickName, String joinPassword) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        tokenUserInfoDto.setCurrentNickName(nickName);
        meetingInfoService.reserveJoinMeeting(meetingId, tokenUserInfoDto, joinPassword);
        return getSuccessResponseVO(meetingId);
    }


    @RequestMapping("/inviteMember")
    @GlobalInterceptor
    public ResponseVO inviteMember(@NotEmpty String selectContactIds) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingInfoService.inviteMember(tokenUserInfoDto, selectContactIds);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/acceptInvite")
    @GlobalInterceptor
    public ResponseVO acceptInvite(@NotEmpty String meetingId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingInfoService.acceptInvite(tokenUserInfoDto, meetingId);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/sendOpenVideoChangeMessage")
    @GlobalInterceptor
    public ResponseVO sendOpenVideoChangeMessage(@NotNull Boolean openVideo) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        this.meetingInfoService.updateMemberOpenVideo(tokenUserInfoDto.getCurrentMeetingId(), tokenUserInfoDto.getUserId(), openVideo);
        return getSuccessResponseVO(null);
    }
}
