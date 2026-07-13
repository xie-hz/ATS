package com.easymeeting.service.impl;

import com.easymeeting.entity.config.AppConfig;
import com.easymeeting.entity.constants.Constants;
import com.easymeeting.entity.dto.MessageSendDto;
import com.easymeeting.entity.dto.TokenUserInfoDto;
import com.easymeeting.entity.enums.*;
import com.easymeeting.entity.po.UserInfo;
import com.easymeeting.entity.query.SimplePage;
import com.easymeeting.entity.query.UserInfoQuery;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.entity.vo.UserInfoVO;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.mappers.UserInfoMapper;
import com.easymeeting.redis.RedisComponet;
import com.easymeeting.service.UserInfoService;
import com.easymeeting.utils.CopyTools;
import com.easymeeting.utils.FFmpegUtils;
import com.easymeeting.utils.StringTools;
import com.easymeeting.websocket.message.MessageHandler;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.Resource;
import java.io.File;
import java.io.IOException;
import java.util.Date;
import java.util.List;


/**
 * 用户信息 业务接口实现
 */
@Service("userInfoService")
public class UserInfoServiceImpl implements UserInfoService {

    @Resource
    private UserInfoMapper<UserInfo, UserInfoQuery> userInfoMapper;

    @Resource
    private RedisComponet redisComponet;

    @Resource
    private AppConfig appConfig;

    @Resource
    private FFmpegUtils fFmpegUtils;

    @Resource
    private MessageHandler messageHandler;

    /**
     * 根据条件查询列表
     */
    @Override
    public List<UserInfo> findListByParam(UserInfoQuery param) {
        return this.userInfoMapper.selectList(param);
    }

    /**
     * 根据条件查询列表
     */
    @Override
    public Integer findCountByParam(UserInfoQuery param) {
        return this.userInfoMapper.selectCount(param);
    }

    /**
     * 分页查询方法
     */
    @Override
    public PaginationResultVO<UserInfo> findListByPage(UserInfoQuery param) {
        int count = this.findCountByParam(param);
        int pageSize = param.getPageSize() == null ? PageSize.SIZE15.getSize() : param.getPageSize();

        SimplePage page = new SimplePage(param.getPageNo(), count, pageSize);
        param.setSimplePage(page);
        List<UserInfo> list = this.findListByParam(param);
        PaginationResultVO<UserInfo> result = new PaginationResultVO(count, page.getPageSize(), page.getPageNo(), page.getPageTotal(), list);
        return result;
    }

    /**
     * 新增
     */
    @Override
    public Integer add(UserInfo bean) {
        return this.userInfoMapper.insert(bean);
    }

    /**
     * 批量新增
     */
    @Override
    public Integer addBatch(List<UserInfo> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.userInfoMapper.insertBatch(listBean);
    }

    /**
     * 批量新增或者修改
     */
    @Override
    public Integer addOrUpdateBatch(List<UserInfo> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.userInfoMapper.insertOrUpdateBatch(listBean);
    }

    /**
     * 多条件更新
     */
    @Override
    public Integer updateByParam(UserInfo bean, UserInfoQuery param) {
        StringTools.checkParam(param);
        return this.userInfoMapper.updateByParam(bean, param);
    }

    /**
     * 多条件删除
     */
    @Override
    public Integer deleteByParam(UserInfoQuery param) {
        StringTools.checkParam(param);
        return this.userInfoMapper.deleteByParam(param);
    }

    /**
     * 根据UserId获取对象
     */
    @Override
    public UserInfo getUserInfoByUserId(String userId) {
        return this.userInfoMapper.selectByUserId(userId);
    }

    /**
     * 根据UserId修改
     */
    @Override
    public Integer updateUserInfoByUserId(UserInfo bean, String userId) {
        return this.userInfoMapper.updateByUserId(bean, userId);
    }

    /**
     * 根据UserId删除
     */
    @Override
    public Integer deleteUserInfoByUserId(String userId) {
        return this.userInfoMapper.deleteByUserId(userId);
    }

    /**
     * 根据Email获取对象
     */
    @Override
    public UserInfo getUserInfoByEmail(String email) {
        return this.userInfoMapper.selectByEmail(email);
    }

    /**
     * 根据Email修改
     */
    @Override
    public Integer updateUserInfoByEmail(UserInfo bean, String email) {
        return this.userInfoMapper.updateByEmail(bean, email);
    }

    /**
     * 根据Email删除
     */
    @Override
    public Integer deleteUserInfoByEmail(String email) {
        return this.userInfoMapper.deleteByEmail(email);
    }

    @Override
    public void register(String email, String nickName, String password) {
        UserInfo userInfo = this.userInfoMapper.selectByEmail(email);
        if (null != userInfo) {
            throw new BusinessException("邮箱账号已经存在");
        }
        Date curDate = new Date();
        String userId = StringTools.getRandomNumber(Constants.LENGTH_12);
        userInfo = new UserInfo();
        userInfo.setUserId(userId);
        userInfo.setNickName(nickName);
        userInfo.setEmail(email);
        userInfo.setPassword(StringTools.encodeByMD5(password));
        userInfo.setCreateTime(curDate);
        userInfo.setStatus(UserStatusEnum.ENABLE.getStatus());
        userInfo.setLastOffTime(curDate.getTime());
        userInfo.setMeetingNo(StringTools.getMeetingNoOrMeetingId());
        this.userInfoMapper.insert(userInfo);
    }

    @Override
    public UserInfoVO login(String email, String password) {
        UserInfo userInfo = this.userInfoMapper.selectByEmail(email);
        if (null == userInfo || !userInfo.getPassword().equals(password)) {
            throw new BusinessException("账号或者密码错误");
        }
        if (UserStatusEnum.DISABLE.getStatus().equals(userInfo.getStatus())) {
            throw new BusinessException("账号已禁用");
        }

        TokenUserInfoDto tokenUserInfoDto = CopyTools.copy(userInfo, TokenUserInfoDto.class);
        Long lastHeartBeat = redisComponet.getUserHeartBeat(tokenUserInfoDto.getUserId());
        if (lastHeartBeat != null) {
            throw new BusinessException("此账号已经在别处登录，请退出后再登录");
        }
        //保存登录信息到redis中
        String token = StringTools.encodeByMD5(tokenUserInfoDto.getUserId() + StringTools.getRandomString(Constants.LENGTH_20));
        tokenUserInfoDto.setToken(token);
        tokenUserInfoDto.setMyMeetingNo(userInfo.getMeetingNo());
        tokenUserInfoDto.setAdmin(appConfig.getAdminEmails().contains(email));

        redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
        UserInfoVO userInfoVO = CopyTools.copy(userInfo, UserInfoVO.class);
        userInfoVO.setToken(token);
        userInfoVO.setAdmin(tokenUserInfoDto.getAdmin());
        return userInfoVO;
    }

    @Override
    public void updateUserInfo(MultipartFile file, UserInfo userInfo) throws IOException {
        if (file != null) {
            String folder = appConfig.getProjectFolder() + Constants.FILE_FOLDER_FILE + Constants.FILE_FOLDER_AVATAR_NAME;
            File folderFile = new File(folder);
            if (!folderFile.exists()) {
                folderFile.mkdirs();
            }
            String realFileName = userInfo.getUserId() + Constants.IMAGE_SUFFIX;
            String filePath = folder + realFileName;
            File tempFile = new File(appConfig.getProjectFolder() + Constants.FILE_FOLDER_TEMP + StringTools.getRandomString(Constants.LENGTH_30));
            file.transferTo(tempFile);
            fFmpegUtils.createImageThumbnail(tempFile, filePath);
        }
        this.userInfoMapper.updateByUserId(userInfo, userInfo.getUserId());
        TokenUserInfoDto tokenUserInfoDto = redisComponet.getTokenUserInfoDtoByUserId(userInfo.getUserId());
        tokenUserInfoDto.setNickName(userInfo.getNickName());
        tokenUserInfoDto.setSex(userInfo.getSex());
        redisComponet.saveTokenUserInfoDto(tokenUserInfoDto);
    }

    @Override
    public void updatePassword(String userId, String oldPassword, String newPassword) {
        UserInfo userInfo = this.userInfoMapper.selectByUserId(userId);
        if (null == userInfo) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        if (!userInfo.getPassword().equals(StringTools.encodeByMD5(oldPassword))) {
            throw new BusinessException("原始密码错误");
        }
        UserInfo updateInfo = new UserInfo();
        updateInfo.setPassword(StringTools.encodeByMD5(newPassword));
        this.userInfoMapper.updateByUserId(updateInfo, userId);
        //清除token
        redisComponet.cleanUserTokenByUserId(userId);
    }

    @Override
    public void updateUserStatus(Integer status, String userId) {
        UserStatusEnum userStatusEnum = UserStatusEnum.getByStatus(status);
        if (userStatusEnum == null) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        UserInfo updateInfo = new UserInfo();
        updateInfo.setStatus(userStatusEnum.getStatus());
        userInfoMapper.updateByUserId(updateInfo, userId);

        //禁用强制下线
        if (userStatusEnum == UserStatusEnum.DISABLE) {
            forceOffLine(userId);
        }
    }

    @Override
    public void forceOffLine(String userId) {
        UserInfo userInfo = this.userInfoMapper.selectByUserId(userId);
        if (Constants.ZERO.equals(userInfo.getOnlineType())) {
            return;
        }
        MessageSendDto sendDto = new MessageSendDto();
        sendDto.setMessageSend2Type(MessageSend2TypeEnum.USER.getType());
        sendDto.setMessageType(MessageTypeEnum.FORCE_OFF_LINE.getType());
        sendDto.setReceiveUserId(userId);
        messageHandler.sendMessage(sendDto);
        redisComponet.cleanUserTokenByUserId(userId);
    }
}