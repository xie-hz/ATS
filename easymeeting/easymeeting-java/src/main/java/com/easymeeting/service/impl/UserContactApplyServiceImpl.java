package com.easymeeting.service.impl;

import com.easymeeting.entity.dto.MessageSendDto;
import com.easymeeting.entity.enums.*;
import com.easymeeting.entity.po.UserContact;
import com.easymeeting.entity.po.UserContactApply;
import com.easymeeting.entity.query.SimplePage;
import com.easymeeting.entity.query.UserContactApplyQuery;
import com.easymeeting.entity.query.UserContactQuery;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.mappers.UserContactApplyMapper;
import com.easymeeting.mappers.UserContactMapper;
import com.easymeeting.service.UserContactApplyService;
import com.easymeeting.utils.StringTools;
import com.easymeeting.websocket.message.MessageHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;


/**
 * 联系人申请 业务接口实现
 */
@Service("userContactApplyService")
public class UserContactApplyServiceImpl implements UserContactApplyService {

    @Resource
    private UserContactApplyMapper<UserContactApply, UserContactApplyQuery> userContactApplyMapper;

    @Resource
    private UserContactMapper<UserContact, UserContactQuery> userContactMapper;
    @Autowired
    private MessageHandler messageHandler;

    /**
     * 根据条件查询列表
     */
    @Override
    public List<UserContactApply> findListByParam(UserContactApplyQuery param) {
        return this.userContactApplyMapper.selectList(param);
    }

    /**
     * 根据条件查询列表
     */
    @Override
    public Integer findCountByParam(UserContactApplyQuery param) {
        return this.userContactApplyMapper.selectCount(param);
    }

    /**
     * 分页查询方法
     */
    @Override
    public PaginationResultVO<UserContactApply> findListByPage(UserContactApplyQuery param) {
        int count = this.findCountByParam(param);
        int pageSize = param.getPageSize() == null ? PageSize.SIZE15.getSize() : param.getPageSize();

        SimplePage page = new SimplePage(param.getPageNo(), count, pageSize);
        param.setSimplePage(page);
        List<UserContactApply> list = this.findListByParam(param);
        PaginationResultVO<UserContactApply> result = new PaginationResultVO(count, page.getPageSize(), page.getPageNo(), page.getPageTotal(), list);
        return result;
    }

    /**
     * 新增
     */
    @Override
    public Integer add(UserContactApply bean) {
        return this.userContactApplyMapper.insert(bean);
    }

    /**
     * 批量新增
     */
    @Override
    public Integer addBatch(List<UserContactApply> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.userContactApplyMapper.insertBatch(listBean);
    }

    /**
     * 批量新增或者修改
     */
    @Override
    public Integer addOrUpdateBatch(List<UserContactApply> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.userContactApplyMapper.insertOrUpdateBatch(listBean);
    }

    /**
     * 多条件更新
     */
    @Override
    public Integer updateByParam(UserContactApply bean, UserContactApplyQuery param) {
        StringTools.checkParam(param);
        return this.userContactApplyMapper.updateByParam(bean, param);
    }

    /**
     * 多条件删除
     */
    @Override
    public Integer deleteByParam(UserContactApplyQuery param) {
        StringTools.checkParam(param);
        return this.userContactApplyMapper.deleteByParam(param);
    }

    /**
     * 根据ApplyId获取对象
     */
    @Override
    public UserContactApply getUserContactApplyByApplyId(Integer applyId) {
        return this.userContactApplyMapper.selectByApplyId(applyId);
    }

    /**
     * 根据ApplyId修改
     */
    @Override
    public Integer updateUserContactApplyByApplyId(UserContactApply bean, Integer applyId) {
        return this.userContactApplyMapper.updateByApplyId(bean, applyId);
    }

    /**
     * 根据ApplyId删除
     */
    @Override
    public Integer deleteUserContactApplyByApplyId(Integer applyId) {
        return this.userContactApplyMapper.deleteByApplyId(applyId);
    }

    /**
     * 根据ApplyUserIdAndReceiveUserId获取对象
     */
    @Override
    public UserContactApply getUserContactApplyByApplyUserIdAndReceiveUserId(String applyUserId, String receiveUserId) {
        return this.userContactApplyMapper.selectByApplyUserIdAndReceiveUserId(applyUserId, receiveUserId);
    }

    /**
     * 根据ApplyUserIdAndReceiveUserId修改
     */
    @Override
    public Integer updateUserContactApplyByApplyUserIdAndReceiveUserId(UserContactApply bean, String applyUserId, String receiveUserId) {
        return this.userContactApplyMapper.updateByApplyUserIdAndReceiveUserId(bean, applyUserId, receiveUserId);
    }

    /**
     * 根据ApplyUserIdAndReceiveUserId删除
     */
    @Override
    public Integer deleteUserContactApplyByApplyUserIdAndReceiveUserId(String applyUserId, String receiveUserId) {
        return this.userContactApplyMapper.deleteByApplyUserIdAndReceiveUserId(applyUserId, receiveUserId);
    }

    @Override
    public Integer saveUserContactApply(UserContactApply bean) {
        //查询对方联系人信息
        UserContact userContact = this.userContactMapper.selectByUserIdAndContactId(bean.getReceiveUserId(), bean.getApplyUserId());
        if (userContact != null && UserContactStatusEnum.BLACKLIST.getStatus().equals(userContact.getStatus())) {
            throw new BusinessException("对方已将你拉黑");
        }

        //对方联系人里，你还是好友，不处理，直接更新自己的联系人
        if (userContact != null && UserContactStatusEnum.FRIEND.getStatus().equals(userContact.getStatus())) {
            UserContact updateInfo = new UserContact();
            updateInfo.setLastUpdateTime(new Date());
            updateInfo.setStatus(UserContactStatusEnum.FRIEND.getStatus());
            userContactMapper.updateByUserIdAndContactId(updateInfo, bean.getApplyUserId(), bean.getReceiveUserId());
            return UserContactStatusEnum.FRIEND.getStatus();
        }

        UserContactApply apply = this.userContactApplyMapper.selectByApplyUserIdAndReceiveUserId(bean.getApplyUserId(), bean.getReceiveUserId());
        if (apply == null) {
            bean.setStatus(UserContactApplyStatusEnum.INIT.getStatus());
            bean.setLastApplyTime(System.currentTimeMillis());
            this.userContactApplyMapper.insert(bean);
        } else {
            UserContactApply updateInfo = new UserContactApply();
            updateInfo.setStatus(UserContactApplyStatusEnum.INIT.getStatus());
            updateInfo.setLastApplyTime(System.currentTimeMillis());
            this.userContactApplyMapper.updateByApplyId(updateInfo, apply.getApplyId());
        }
        //发消息通知对方
        MessageSendDto messageSendDto = new MessageSendDto();
        messageSendDto.setMessageSend2Type(MessageSend2TypeEnum.USER.getType());
        messageSendDto.setMessageType(MessageTypeEnum.USER_CONTACT_APPLY.getType());
        messageSendDto.setReceiveUserId(bean.getReceiveUserId());
        messageHandler.sendMessage(messageSendDto);
        return UserContactApplyStatusEnum.INIT.getStatus();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void dealWithApply(String applyUserId, String userId, String nickName, Integer status) {
        UserContactApplyStatusEnum statusEnum = UserContactApplyStatusEnum.getByStatus(status);
        if (statusEnum == null || UserContactApplyStatusEnum.INIT == statusEnum) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        UserContactApply apply = this.userContactApplyMapper.selectByApplyUserIdAndReceiveUserId(applyUserId, userId);
        if (apply == null) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        if (UserContactApplyStatusEnum.PASS.getStatus().equals(status)) {
            Date now = new Date();
            UserContact userContact = new UserContact();
            userContact.setUserId(applyUserId);
            userContact.setContactId(userId);
            userContact.setStatus(UserContactStatusEnum.FRIEND.getStatus());
            userContact.setLastUpdateTime(now);
            userContactMapper.insertOrUpdate(userContact);
            userContact.setUserId(userId);
            userContact.setContactId(applyUserId);
            userContactMapper.insertOrUpdate(userContact);
        }
        UserContactApply updateApply = new UserContactApply();
        updateApply.setStatus(status);
        this.userContactApplyMapper.updateByApplyId(updateApply, apply.getApplyId());
        /**
         * 发送消息
         */
        MessageSendDto sendDto = new MessageSendDto();
        sendDto.setMessageSend2Type(MessageSend2TypeEnum.USER.getType());
        sendDto.setMessageType(MessageTypeEnum.USER_CONTACT_DEAL_WITH.getType());
        sendDto.setReceiveUserId(applyUserId);
        sendDto.setSendUserId(userId);
        sendDto.setSendUserNickName(nickName);
        sendDto.setMessageContent(status);
        messageHandler.sendMessage(sendDto);
    }
}