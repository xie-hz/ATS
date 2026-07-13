package com.easymeeting.controller;

import com.easymeeting.annotation.GlobalInterceptor;
import com.easymeeting.redis.RedisComponet;
import com.easymeeting.entity.dto.SysSettingDto;
import com.easymeeting.entity.vo.ResponseVO;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;

@RestController
@RequestMapping("/admin")
public class AdminSettingController extends ABaseController {

    @Resource
    private RedisComponet redisComponet;

    @RequestMapping("/saveSysSetting")
    @GlobalInterceptor(checkAdmin = true)
    public ResponseVO saveSysSetting(SysSettingDto sysSettingDto) {
        redisComponet.saveSysSetting(sysSettingDto);
        return getSuccessResponseVO(null);
    }

    @RequestMapping("/getSysSetting")
    @GlobalInterceptor(checkAdmin = true)
    public ResponseVO getSysSetting() {
        SysSettingDto sysSettingDto = redisComponet.getSysSetting();
        return getSuccessResponseVO(sysSettingDto);
    }
}
