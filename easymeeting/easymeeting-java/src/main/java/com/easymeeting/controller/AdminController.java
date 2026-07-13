package com.easymeeting.controller;

import com.easymeeting.annotation.GlobalInterceptor;
import com.easymeeting.entity.query.UserInfoQuery;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.service.UserInfoService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;

@RestController
@RequestMapping("/admin")
@Validated
public class AdminController extends ABaseController {

    @Resource
    private UserInfoService userInfoService;

    @RequestMapping(value = "/loadUserList")
    @GlobalInterceptor
    public ResponseVO loadUserList(String nickNameFuzzy, Integer pageNo, Integer pageSize) {
        UserInfoQuery userInfoQuery = new UserInfoQuery();
        userInfoQuery.setNickNameFuzzy(nickNameFuzzy);
        userInfoQuery.setPageNo(pageNo);
        userInfoQuery.setPageSize(pageSize);
        PaginationResultVO resultVO = this.userInfoService.findListByPage(userInfoQuery);
        return getSuccessResponseVO(resultVO);
    }

    @RequestMapping("/updateUserStatus")
    @GlobalInterceptor(checkAdmin = true)
    public ResponseVO updateUserStatus(@NotNull Integer status,
                                       @NotEmpty String userId) {
        userInfoService.updateUserStatus(status, userId);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/forceOffLine")
    @GlobalInterceptor(checkAdmin = true)
    public ResponseVO forceOffLine(@NotEmpty String userId) {
        userInfoService.forceOffLine(userId);
        return getSuccessResponseVO(null);
    }
}
