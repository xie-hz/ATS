package com.easymeeting.service;

import com.easymeeting.entity.po.MeetingReserve;
import com.easymeeting.entity.query.MeetingReserveQuery;
import com.easymeeting.entity.vo.PaginationResultVO;

import java.util.List;


/**
 * 会议预约 业务接口
 */
public interface MeetingReserveService {

    /**
     * 根据条件查询列表
     */
    List<MeetingReserve> findListByParam(MeetingReserveQuery param);

    /**
     * 根据条件查询列表
     */
    Integer findCountByParam(MeetingReserveQuery param);

    /**
     * 分页查询
     */
    PaginationResultVO<MeetingReserve> findListByPage(MeetingReserveQuery param);

    /**
     * 新增
     */
    Integer add(MeetingReserve bean);

    /**
     * 批量新增
     */
    Integer addBatch(List<MeetingReserve> listBean);

    /**
     * 批量新增/修改
     */
    Integer addOrUpdateBatch(List<MeetingReserve> listBean);

    /**
     * 多条件更新
     */
    Integer updateByParam(MeetingReserve bean, MeetingReserveQuery param);

    /**
     * 多条件删除
     */
    Integer deleteByParam(MeetingReserveQuery param);

    /**
     * 根据MeetingId查询对象
     */
    MeetingReserve getMeetingReserveByMeetingId(String meetingId);


    /**
     * 根据MeetingId修改
     */
    Integer updateMeetingReserveByMeetingId(MeetingReserve bean, String meetingId);


    /**
     * 根据MeetingId删除
     */
    Integer deleteMeetingReserveByMeetingId(String meetingId);

    void saveMeetingReserve(MeetingReserve bean);

    void deleteMeetingReserve(String meetingId, String userId);

    void delMeetingReserveByUser(String meetingId, String userId);
}