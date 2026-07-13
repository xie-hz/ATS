package com.easymeeting.controller;

import com.easymeeting.annotation.GlobalInterceptor;
import com.easymeeting.entity.dto.SysSettingDto;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.po.UserInfo;
import com.easymeeting.entity.vo.CheckCodeVO;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.entity.vo.SysSettingVO;
import com.easymeeting.entity.vo.UserInfoVO;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.redis.RedisComponet;
import com.easymeeting.service.UserInfoService;
import com.easymeeting.utils.CopyTools;
import com.wf.captcha.SpecCaptcha;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.Resource;
import javax.validation.constraints.Email;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;
import java.io.IOException;

@RestController("accountController")
@RequestMapping("/account")
@Validated
public class AccountController extends ABaseController {

    @Resource
    private RedisComponet redisComponet;

    @Resource
    private UserInfoService userInfoService;

    /**
     * 验证码
     */
    @RequestMapping(value = "/checkCode")
    public ResponseVO checkCode() {
        // 用 SpecCaptcha（随机字符）替代 ArithmeticCaptcha：算术验证码依赖
        // javax.script.ScriptEngine(Nashorn)，Java 15+ 已移除，在 Java 21 上会 NPE。
        SpecCaptcha captcha = new SpecCaptcha(100, 42);
        String code = captcha.text().toLowerCase();
        String checkCodeKey = redisComponet.saveCheckCode(code);
        String checkCodeBase64 = captcha.toBase64();
        CheckCodeVO checkCodeVO = new CheckCodeVO();
        checkCodeVO.setCheckCode(checkCodeBase64);
        checkCodeVO.setCheckCodeKey(checkCodeKey);
        return getSuccessResponseVO(checkCodeVO);
    }

    @RequestMapping(value = "/register")
    public ResponseVO register(@NotEmpty String checkCodeKey, @NotEmpty @Email String email, @NotEmpty String password, @NotEmpty String nickName,
                               @NotEmpty String checkCode) {
        try {
            if (!checkCode.equalsIgnoreCase(redisComponet.getCheckCode(checkCodeKey))) {
                throw new BusinessException("图片验证码不正确");
            }
            userInfoService.register(email, nickName, password);
            return getSuccessResponseVO(null);
        } finally {
            redisComponet.cleanCheckCode(checkCodeKey);
        }
    }

    @RequestMapping(value = "/login")
    public ResponseVO login(@NotEmpty String checkCodeKey, @NotEmpty @Email String email, @NotEmpty String password, @NotEmpty String checkCode) {
        try {
            if (!checkCode.equalsIgnoreCase(redisComponet.getCheckCode(checkCodeKey))) {
                throw new BusinessException("图片验证码不正确");
            }
            UserInfoVO userInfoVO = userInfoService.login(email, password);
            return getSuccessResponseVO(userInfoVO);
        } finally {
            redisComponet.cleanCheckCode(checkCodeKey);
        }
    }

    @RequestMapping(value = "/logout")
    public ResponseVO logout() {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        if (tokenUserInfoDto == null) {
            return getSuccessResponseVO(null);
        }
        UserInfo userInfo = new UserInfo();
        userInfo.setLastOffTime(System.currentTimeMillis());
        userInfoService.updateUserInfoByUserId(userInfo, tokenUserInfoDto.getUserId());
        redisComponet.cleanUserTokenByUserId(tokenUserInfoDto.getUserId());
        return getSuccessResponseVO(null);
    }

    @RequestMapping(value = "/updateUserInfo")
    @GlobalInterceptor
    public ResponseVO updateUserInfo(MultipartFile avatar, @NotEmpty String nickName, @NotNull Integer sex) throws IOException {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        UserInfo userInfo = new UserInfo();
        userInfo.setNickName(nickName);
        userInfo.setSex(sex);
        userInfo.setUserId(tokenUserInfoDto.getUserId());
        userInfoService.updateUserInfo(avatar, userInfo);
        return getSuccessResponseVO(null);
    }

    @RequestMapping(value = "/updatePassword")
    @GlobalInterceptor
    public ResponseVO updatePassword(@NotEmpty String oldPassword, @NotEmpty String password) {
        TokenUserInfoDto tokenUserInfoDto = getTokenUserInfo();
        userInfoService.updatePassword(tokenUserInfoDto.getUserId(), oldPassword, password);
        return getSuccessResponseVO(null);
    }

    @RequestMapping(value = "/getSysSetting")
    @GlobalInterceptor
    public ResponseVO getSysSetting() {
        SysSettingDto sysSettingDto = redisComponet.getSysSetting();
        return getSuccessResponseVO(CopyTools.copy(sysSettingDto, SysSettingVO.class));
    }
}