package com.easymeeting.service.impl;

import com.easymeeting.entity.enums.PageSize;
import com.easymeeting.entity.enums.ResponseCodeEnum;
import com.easymeeting.entity.enums.UserContactApplyStatusEnum;
import com.easymeeting.entity.enums.UserContactStatusEnum;
import com.easymeeting.entity.po.UserContact;
import com.easymeeting.entity.po.UserContactApply;
import com.easymeeting.entity.po.UserInfo;
import com.easymeeting.entity.query.SimplePage;
import com.easymeeting.entity.query.UserContactApplyQuery;
import com.easymeeting.entity.query.UserContactQuery;
import com.easymeeting.entity.query.UserInfoQuery;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.entity.vo.UserInfoVO4Search;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.mappers.UserContactApplyMapper;
import com.easymeeting.mappers.UserContactMapper;
import com.easymeeting.mappers.UserInfoMapper;
import com.easymeeting.service.UserContactService;
import com.easymeeting.utils.StringTools;
import org.apache.commons.lang3.ArrayUtils;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;


/**
 * 联系人 业务接口实现
 */
@Service("userContactService")
public class UserContactServiceImpl implements UserContactService {

    @Resource
    private UserContactMapper<UserContact, UserContactQuery> userContactMapper;

    @Resource
    private UserInfoMapper<UserInfo, UserInfoQuery> userInfoMapper;

    @Resource
    private UserContactApplyMapper<UserContactApply, UserContactApplyQuery> userContactApplyMapper;

    /**
     * 根据条件查询列表
     */
    @Override
    public List<UserContact> findListByParam(UserContactQuery param) {
        return this.userContactMapper.selectList(param);
    }

    /**
     * 根据条件查询列表
     */
    @Override
    public Integer findCountByParam(UserContactQuery param) {
        return this.userContactMapper.selectCount(param);
    }

    /**
     * 分页查询方法
     */
    @Override
    public PaginationResultVO<UserContact> findListByPage(UserContactQuery param) {
        int count = this.findCountByParam(param);
        int pageSize = param.getPageSize() == null ? PageSize.SIZE15.getSize() : param.getPageSize();

        SimplePage page = new SimplePage(param.getPageNo(), count, pageSize);
        param.setSimplePage(page);
        List<UserContact> list = this.findListByParam(param);
        PaginationResultVO<UserContact> result = new PaginationResultVO(count, page.getPageSize(), page.getPageNo(), page.getPageTotal(), list);
        return result;
    }

    /**
     * 新增
     */
    @Override
    public Integer add(UserContact bean) {
        return this.userContactMapper.insert(bean);
    }

    /**
     * 批量新增
     */
    @Override
    public Integer addBatch(List<UserContact> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.userContactMapper.insertBatch(listBean);
    }

    /**
     * 批量新增或者修改
     */
    @Override
    public Integer addOrUpdateBatch(List<UserContact> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.userContactMapper.insertOrUpdateBatch(listBean);
    }

    /**
     * 多条件更新
     */
    @Override
    public Integer updateByParam(UserContact bean, UserContactQuery param) {
        StringTools.checkParam(param);
        return this.userContactMapper.updateByParam(bean, param);
    }

    /**
     * 多条件删除
     */
    @Override
    public Integer deleteByParam(UserContactQuery param) {
        StringTools.checkParam(param);
        return this.userContactMapper.deleteByParam(param);
    }

    /**
     * 根据UserIdAndContactId获取对象
     */
    @Override
    public UserContact getUserContactByUserIdAndContactId(String userId, String contactId) {
        return this.userContactMapper.selectByUserIdAndContactId(userId, contactId);
    }

    /**
     * 根据UserIdAndContactId修改
     */
    @Override
    public Integer updateUserContactByUserIdAndContactId(UserContact bean, String userId, String contactId) {
        return this.userContactMapper.updateByUserIdAndContactId(bean, userId, contactId);
    }

    /**
     * 根据UserIdAndContactId删除
     */
    @Override
    public Integer deleteUserContactByUserIdAndContactId(String userId, String contactId) {
        return this.userContactMapper.deleteByUserIdAndContactId(userId, contactId);
    }

    @Override
    public UserInfoVO4Search searchContact(String myUserId, String userId) {
        UserInfo userInfo = userInfoMapper.selectByUserId(userId);
        if (userInfo == null) {
            return null;
        }
        UserInfoVO4Search result = new UserInfoVO4Search();
        result.setUserId(userInfo.getUserId());
        result.setNickName(userInfo.getNickName());
        //是自己
        if (myUserId.equals(userId)) {
            result.setStatus(-UserContactApplyStatusEnum.PASS.getStatus());
            return result;
        }
        //查询状态
        UserContactApply contactApply = userContactApplyMapper.selectByApplyUserIdAndReceiveUserId(myUserId, userId);

        //查询好友的联系人
        UserContact userContact = userContactMapper.selectByUserIdAndContactId(userId, myUserId);
        //被拉黑
        if (contactApply != null && UserContactApplyStatusEnum.BLACKLIST.getStatus().equals(contactApply.getStatus())
                || userContact != null && UserContactStatusEnum.BLACKLIST.getStatus().equals(userContact.getStatus())) {
            result.setStatus(UserContactApplyStatusEnum.BLACKLIST.getStatus());
            return result;
        }
        //已经申请 待处理
        if (contactApply != null && UserContactApplyStatusEnum.INIT.getStatus().equals(contactApply.getStatus())) {
            result.setStatus(UserContactApplyStatusEnum.INIT.getStatus());
            return result;
        }
        //已经是好友，双方都是好友
        UserContact myUserContact = userContactMapper.selectByUserIdAndContactId(myUserId, userId);
        if (userContact != null && UserContactStatusEnum.FRIEND.getStatus().equals(userContact.getStatus()) &&
                myUserContact != null && UserContactStatusEnum.FRIEND.getStatus().equals(myUserContact.getStatus())) {
            result.setStatus(UserContactStatusEnum.FRIEND.getStatus());
            return result;
        }
        return result;
    }

    @Override
    public void delContact(String userId, String contactId, Integer status) {
        if (!ArrayUtils.contains(new Integer[]{UserContactStatusEnum.DEL.getStatus(), UserContactStatusEnum.BLACKLIST.getStatus()}, status)) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        UserContact userContact = new UserContact();
        userContact.setLastUpdateTime(new Date());
        userContact.setStatus(status);
        this.userContactMapper.updateByUserIdAndContactId(userContact, userId, contactId);
    }

}