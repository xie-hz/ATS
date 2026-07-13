package com.easymeeting.controller;

import com.easymeeting.annotation.GlobalInterceptor;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.DateTimePatternEnum;
import com.easymeeting.entity.enums.MeetingReserveStatusEnum;
import com.easymeeting.entity.po.MeetingReserve;
import com.easymeeting.entity.query.MeetingReserveQuery;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.service.MeetingReserveService;
import com.easymeeting.utils.DateUtil;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.validation.constraints.NotEmpty;
import java.util.Date;

/**
 * 会议预约 Controller
 */
@RestController("meetingReserveController")
@RequestMapping("/meetingReserve")
@Validated
public class MeetingReserveController extends ABaseController {

    @Resource
    private MeetingReserveService meetingReserveService;

    /**
     * 根据条件分页查询
     */
    @RequestMapping("/loadMeetingReserve")
    @GlobalInterceptor
    public ResponseVO loadMeetingReserve() {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        MeetingReserveQuery query = new MeetingReserveQuery();
        query.setUserId(tokenUserInfoDto.getUserId());
        query.setOrderBy("start_time desc");
        query.setStatus(MeetingReserveStatusEnum.NO_START.getStatus());
        query.setQueryUserInfo(true);
        return getSuccessResponseVO(meetingReserveService.findListByPage(query));
    }

    @RequestMapping("/createMeetingReserve")
    @GlobalInterceptor
    public ResponseVO createMeetingReserve(MeetingReserve meetingReserve) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingReserve.setCreateUserId(tokenUserInfoDto.getUserId());
        meetingReserveService.saveMeetingReserve(meetingReserve);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/delMeetingReserve")
    @GlobalInterceptor
    public ResponseVO delMeetingReserve(@NotEmpty String meetingId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingReserveService.deleteMeetingReserve(meetingId, tokenUserInfoDto.getUserId());
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/loadTodayMeeting")
    @GlobalInterceptor
    public ResponseVO loadTodayMeeting() {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        MeetingReserveQuery meetingReserveQuery = new MeetingReserveQuery();
        meetingReserveQuery.setUserId(tokenUserInfoDto.getUserId());
        String curDate = DateUtil.format(new Date(), DateTimePatternEnum.YYYY_MM_DD.getPattern());
        meetingReserveQuery.setStartTimeStart(curDate);
        meetingReserveQuery.setStartTimeEnd(curDate);
        meetingReserveQuery.setStatus(MeetingReserveStatusEnum.NO_START.getStatus());
        meetingReserveQuery.setOrderBy("start_time asc");
        return getSuccessResponseVO(meetingReserveService.findListByParam(meetingReserveQuery));
    }

    @RequestMapping("/delMeetingReserveByUser")
    @GlobalInterceptor
    public ResponseVO delMeetingReserveByUser(@NotEmpty String meetingId) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        meetingReserveService.delMeetingReserveByUser(meetingId, tokenUserInfoDto.getUserId());
        return getSuccessResponseVO(null);
    }
}