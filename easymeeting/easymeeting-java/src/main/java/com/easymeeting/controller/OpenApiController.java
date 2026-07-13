package com.easymeeting.controller;

import com.easymeeting.entity.config.AppConfig;
import com.easymeeting.entity.po.MeetingInfo;
import com.easymeeting.entity.po.UserInfo;
import com.easymeeting.entity.query.UserInfoQuery;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.mappers.UserInfoMapper;
import com.easymeeting.service.AtsWebhookService;
import com.easymeeting.service.MeetingInfoService;
import com.easymeeting.utils.StringTools;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.validation.constraints.NotEmpty;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 开放接口：供 ATS 等外部系统通过服务账号 API Key 调用，
 * 创建/查询/取消面试会议。
 *
 * 鉴权：请求头 X-API-Key 与配置 openapi.apikey 比对。
 */
@RestController
@RequestMapping("/openapi/meeting")
public class OpenApiController extends ABaseController {

    @Resource
    private AppConfig appConfig;

    @Resource
    private MeetingInfoService meetingInfoService;

    @Resource
    private AtsWebhookService atsWebhookService;

    @Resource
    private UserInfoMapper<UserInfo, UserInfoQuery> userInfoMapper;

    /**
     * 创建面试会议（代建模式）
     * hostEmail: 当前 HR 的邮箱，在 user_info 查 userId 作为主持人。
     *            找不到则回退到 admin（admin.emails 配置的第一个）。
     * startTime: 面试预约时间（yyyy-MM-dd HH:mm:ss），用于计算 1 小时窗口
     */
    @RequestMapping("/create")
    public ResponseVO create(
            @RequestHeader(value = "X-API-Key", required = false) String apiKey,
            @NotEmpty String hostEmail,
            @NotEmpty String meetingName,
            Integer joinType,
            String joinPassword,
            String atsBusinessId,
            String startTime) {
        checkApiKey(apiKey);
        // 根据 hostEmail 解析 hostUserId
        String hostUserId = resolveHostUserId(hostEmail);
        java.util.Date startDate = null;
        if (startTime != null && !startTime.isEmpty()) {
            try {
                startDate = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(startTime);
            } catch (Exception e) {
                // 格式不对就用当前时间
            }
        }
        MeetingInfo meetingInfo = meetingInfoService.createInterviewMeeting(
                hostUserId, meetingName, joinType, joinPassword, atsBusinessId, startDate);
        Map<String, Object> result = new HashMap<>();
        result.put("meetingId", meetingInfo.getMeetingId());
        result.put("meetingNo", meetingInfo.getMeetingNo());
        result.put("joinPassword", meetingInfo.getJoinPassword());
        result.put("hostUserId", meetingInfo.getCreateUserId());
        return getSuccessResponseVO(result);
    }

    /**
     * 根据邮箱查找 EasyMeeting userId：
     * 1. 先查 hostEmail -> 找到则用该 userId
     * 2. 找不到 -> 查 admin.emails 的第一个邮箱 -> 找到则用 admin userId
     * 3. 都找不到 -> 用 "HR_DEFAULT"
     */
    private String resolveHostUserId(String hostEmail) {
        // 1. 查 hostEmail
        if (!StringTools.isEmpty(hostEmail)) {
            UserInfoQuery query = new UserInfoQuery();
            query.setEmail(hostEmail);
            List<UserInfo> users = userInfoMapper.selectList(query);
            if (users != null && !users.isEmpty()) {
                return users.get(0).getUserId();
            }
        }
        // 2. 回退到 admin
        String adminEmails = appConfig.getAdminEmails();
        if (!StringTools.isEmpty(adminEmails)) {
            String firstAdminEmail = adminEmails.split(",")[0].trim();
            UserInfoQuery adminQuery = new UserInfoQuery();
            adminQuery.setEmail(firstAdminEmail);
            List<UserInfo> admins = userInfoMapper.selectList(adminQuery);
            if (admins != null && !admins.isEmpty()) {
                return admins.get(0).getUserId();
            }
        }
        // 3. 兜底
        return "HR_DEFAULT";
    }

    /**
     * 查询会议信息
     */
    @RequestMapping("/query")
    public ResponseVO query(
            @RequestHeader(value = "X-API-Key", required = false) String apiKey,
            @NotEmpty String meetingId) {
        checkApiKey(apiKey);
        MeetingInfo meetingInfo = meetingInfoService.getMeetingInfoByMeetingId(meetingId);
        return getSuccessResponseVO(meetingInfo);
    }

    /**
     * 取消会议（结束会议并通知 ATS）
     */
    @RequestMapping("/cancel")
    public ResponseVO cancel(
            @RequestHeader(value = "X-API-Key", required = false) String apiKey,
            @NotEmpty String meetingId) {
        checkApiKey(apiKey);
        MeetingInfo meetingInfo = meetingInfoService.getMeetingInfoByMeetingId(meetingId);
        if (meetingInfo == null) {
            throw new BusinessException("会议不存在");
        }
        // null userId 跳过创建人校验（服务账号代操作）
        meetingInfoService.finishMeeting(meetingId, null);
        atsWebhookService.notifyMeetingEvent(meetingInfo, "CANCELLED");
        return getSuccessResponseVO(null);
    }

    private void checkApiKey(String apiKey) {
        String configKey = appConfig.getOpenApiApiKey();
        if (configKey == null || configKey.isEmpty() || !configKey.equals(apiKey)) {
            throw new BusinessException("无效的API Key");
        }
    }
}
