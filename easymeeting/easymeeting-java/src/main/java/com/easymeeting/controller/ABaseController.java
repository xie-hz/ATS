package com.easymeeting.controller;

import com.easymeeting.redis.RedisComponet;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.ResponseCodeEnum;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.exception.BusinessException;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;


public class ABaseController {

    protected static final String STATUC_SUCCESS = "success";

    protected static final String STATUC_ERROR = "error";

    @Resource
    private RedisComponet redisComponet;

    protected <T> ResponseVO getSuccessResponseVO(T t) {
        ResponseVO<T> responseVO = new ResponseVO<>();
        responseVO.setStatus(STATUC_SUCCESS);
        responseVO.setCode(ResponseCodeEnum.CODE_200.getCode());
        responseVO.setInfo(ResponseCodeEnum.CODE_200.getMsg());
        responseVO.setData(t);
        return responseVO;
    }

    protected <T> ResponseVO getBusinessErrorResponseVO(BusinessException e, T t) {
        ResponseVO vo = new ResponseVO();
        vo.setStatus(STATUC_ERROR);
        if (e.getCode() == null) {
            vo.setCode(ResponseCodeEnum.CODE_600.getCode());
        } else {
            vo.setCode(e.getCode());
        }
        vo.setInfo(e.getMessage());
        vo.setData(t);
        return vo;
    }

    protected <T> ResponseVO getServerErrorResponseVO(T t) {
        ResponseVO vo = new ResponseVO();
        vo.setStatus(STATUC_ERROR);
        vo.setCode(ResponseCodeEnum.CODE_500.getCode());
        vo.setInfo(ResponseCodeEnum.CODE_500.getMsg());
        vo.setData(t);
        return vo;
    }

    protected TokenUserInfoDto getTokenUserInfo() {
        HttpServletRequest request = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();
        String token = request.getHeader("token");
        TokenUserInfoDto tokenUserInfoDto = redisComponet.getTokenUserInfoDto(token);
        return tokenUserInfoDto;
    }

    protected TokenUserInfoDto getTokenUserInfo(String token) {
        TokenUserInfoDto tokenUserInfoDto = redisComponet.getTokenUserInfoDto(token);
        return tokenUserInfoDto;
    }

    protected void resetTokenUserInfo(TokenUserInfoDto tokenUserInfoDto) {
        redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
    }
}
