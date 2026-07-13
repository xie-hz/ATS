package com.easymeeting.controller;

import com.easymeeting.annotation.GlobalInterceptor;
import com.easymeeting.entity.query.MeetingInfoQuery;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.service.MeetingInfoService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.validation.constraints.NotEmpty;

@Validated
@RestController
@RequestMapping("/admin")
public class AdminMeetingInfoController extends ABaseController {

    @Resource
    private MeetingInfoService meetingInfoService;

    @RequestMapping("/loadAdminMeeting")
    @GlobalInterceptor
    public ResponseVO loadMeeting(String meetingNameFuzzy, Integer pageNo, Integer pageSize) {
        MeetingInfoQuery infoQuery = new MeetingInfoQuery();
        infoQuery.setMeetingNameFuzzy(meetingNameFuzzy);
        infoQuery.setPageNo(pageNo);
        infoQuery.setPageSize(pageSize);
        infoQuery.setOrderBy("m.create_time desc");
        infoQuery.setQueryMemberCount(true);
        PaginationResultVO resultVO = this.meetingInfoService.findListByPage(infoQuery);
        return getSuccessResponseVO(resultVO);
    }

    @RequestMapping("/adminFinishMeeting")
    @GlobalInterceptor
    public ResponseVO adminFinishMeeting(@NotEmpty String meetingId) {
        this.meetingInfoService.finishMeeting(meetingId, null);
        return getSuccessResponseVO(null);
    }
}
