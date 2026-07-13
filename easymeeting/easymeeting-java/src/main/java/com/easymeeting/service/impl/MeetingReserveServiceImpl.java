package com.easymeeting.service.impl;

import com.easymeeting.entity.enums.MeetingReserveStatusEnum;
import com.easymeeting.entity.enums.PageSize;
import com.easymeeting.entity.enums.ResponseCodeEnum;
import com.easymeeting.entity.po.MeetingInfo;
import com.easymeeting.entity.po.MeetingReserve;
import com.easymeeting.entity.po.MeetingReserveMember;
import com.easymeeting.entity.query.MeetingInfoQuery;
import com.easymeeting.entity.query.MeetingReserveMemberQuery;
import com.easymeeting.entity.query.MeetingReserveQuery;
import com.easymeeting.entity.query.SimplePage;
import com.easymeeting.entity.vo.PaginationResultVO;
import com.easymeeting.exception.BusinessException;
import com.easymeeting.mappers.MeetingInfoMapper;
import com.easymeeting.mappers.MeetingReserveMapper;
import com.easymeeting.mappers.MeetingReserveMemberMapper;
import com.easymeeting.service.MeetingReserveService;
import com.easymeeting.utils.StringTools;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;


/**
 * 会议预约 业务接口实现
 */
@Service("meetingReserveService")
public class MeetingReserveServiceImpl implements MeetingReserveService {

    @Resource
    private MeetingReserveMapper<MeetingReserve, MeetingReserveQuery> meetingReserveMapper;

    @Resource
    private MeetingReserveMemberMapper<MeetingReserveMember, MeetingReserveMemberQuery> meetingReserveMemberMapper;

    @Resource
    private MeetingInfoMapper<MeetingInfo, MeetingInfoQuery> meetingInfoMapper;

    /**
     * 根据条件查询列表
     */
    @Override
    public List<MeetingReserve> findListByParam(MeetingReserveQuery param) {
        return this.meetingReserveMapper.selectList(param);
    }

    /**
     * 根据条件查询列表
     */
    @Override
    public Integer findCountByParam(MeetingReserveQuery param) {
        return this.meetingReserveMapper.selectCount(param);
    }

    /**
     * 分页查询方法
     */
    @Override
    public PaginationResultVO<MeetingReserve> findListByPage(MeetingReserveQuery param) {
        int count = this.findCountByParam(param);
        int pageSize = param.getPageSize() == null ? PageSize.SIZE15.getSize() : param.getPageSize();

        SimplePage page = new SimplePage(param.getPageNo(), count, pageSize);
        param.setSimplePage(page);
        List<MeetingReserve> list = this.findListByParam(param);
        PaginationResultVO<MeetingReserve> result = new PaginationResultVO(count, page.getPageSize(), page.getPageNo(), page.getPageTotal(), list);
        return result;
    }

    /**
     * 新增
     */
    @Override
    public Integer add(MeetingReserve bean) {
        return this.meetingReserveMapper.insert(bean);
    }

    /**
     * 批量新增
     */
    @Override
    public Integer addBatch(List<MeetingReserve> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.meetingReserveMapper.insertBatch(listBean);
    }

    /**
     * 批量新增或者修改
     */
    @Override
    public Integer addOrUpdateBatch(List<MeetingReserve> listBean) {
        if (listBean == null || listBean.isEmpty()) {
            return 0;
        }
        return this.meetingReserveMapper.insertOrUpdateBatch(listBean);
    }

    /**
     * 多条件更新
     */
    @Override
    public Integer updateByParam(MeetingReserve bean, MeetingReserveQuery param) {
        StringTools.checkParam(param);
        return this.meetingReserveMapper.updateByParam(bean, param);
    }

    /**
     * 多条件删除
     */
    @Override
    public Integer deleteByParam(MeetingReserveQuery param) {
        StringTools.checkParam(param);
        return this.meetingReserveMapper.deleteByParam(param);
    }

    /**
     * 根据MeetingId获取对象
     */
    @Override
    public MeetingReserve getMeetingReserveByMeetingId(String meetingId) {
        return this.meetingReserveMapper.selectByMeetingId(meetingId);
    }

    /**
     * 根据MeetingId修改
     */
    @Override
    public Integer updateMeetingReserveByMeetingId(MeetingReserve bean, String meetingId) {
        return this.meetingReserveMapper.updateByMeetingId(bean, meetingId);
    }

    /**
     * 根据MeetingId删除
     */
    @Override
    public Integer deleteMeetingReserveByMeetingId(String meetingId) {
        return this.meetingReserveMapper.deleteByMeetingId(meetingId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void saveMeetingReserve(MeetingReserve bean) {
        bean.setMeetingId(StringTools.getMeetingNoOrMeetingId());
        bean.setCreateTime(new Date());
        bean.setStatus(MeetingReserveStatusEnum.NO_START.getStatus());
        this.meetingReserveMapper.insertOrUpdate(bean);

        List<MeetingReserveMember> meetingReserveMembersList = new ArrayList<>();
        if (!StringTools.isEmpty(bean.getInviteUserIds())) {
            String[] inviteUserIdArray = bean.getInviteUserIds().split(",");
            for (String userId : inviteUserIdArray) {
                MeetingReserveMember member = new MeetingReserveMember();
                member.setMeetingId(bean.getMeetingId());
                member.setInviteUserId(userId);
                meetingReserveMembersList.add(member);
            }
        }
        //自己加入进去
        MeetingReserveMember member = new MeetingReserveMember();
        member.setMeetingId(bean.getMeetingId());
        member.setInviteUserId(bean.getCreateUserId());
        meetingReserveMembersList.add(member);
        meetingReserveMemberMapper.insertBatch(meetingReserveMembersList);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteMeetingReserve(String meetingId, String userId) {
        MeetingReserveQuery reserveQuery = new MeetingReserveQuery();
        reserveQuery.setMeetingId(meetingId);
        reserveQuery.setCreateUserId(userId);
        Integer count = meetingReserveMapper.deleteByParam(reserveQuery);
        if (count > 0) {
            MeetingReserveMemberQuery memberQuery = new MeetingReserveMemberQuery();
            memberQuery.setMeetingId(meetingId);
            this.meetingReserveMemberMapper.deleteByParam(memberQuery);
        }
    }

    @Override
    public void delMeetingReserveByUser(String meetingId, String userId) {
        MeetingReserve meetingInfo = this.meetingReserveMapper.selectByMeetingId(meetingId);
        if (meetingInfo == null) {
            throw new BusinessException(ResponseCodeEnum.CODE_600);
        }
        if (meetingInfo.getCreateUserId().equals(userId)) {
            deleteMeetingReserve(meetingId, userId);
        } else {
            MeetingReserveMemberQuery memberQuery = new MeetingReserveMemberQuery();
            memberQuery.setMeetingId(meetingId);
            memberQuery.setInviteUserId(userId);
            this.meetingReserveMemberMapper.deleteByParam(memberQuery);
        }
    }
}