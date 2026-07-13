package com.easymeeting.controller;

import com.easymeeting.annotation.GlobalInterceptor;
import com.easymeeting.entity.config.AppConfig;
import com.easymeeting.entity.constants.Constants;
import com.easymeeting.entity.po.AppUpdate;
import com.easymeeting.entity.vo.AppUpdateVO;
import com.easymeeting.entity.vo.ResponseVO;
import com.easymeeting.service.AppUpdateService;
import com.easymeeting.utils.CopyTools;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletResponse;
import javax.validation.constraints.NotNull;
import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.util.Arrays;

@RestController("updateController")
@RequestMapping("/update")
@Validated
public class UpdateController extends ABaseController {

    private static final Logger logger = LoggerFactory.getLogger(UpdateController.class);

    @Resource
    private AppConfig appConfig;

    @Resource
    private AppUpdateService appUpdateService;

    @RequestMapping("/checkVersion")
    @GlobalInterceptor
    public ResponseVO checkVersion(String appVersion, String uid) {
        AppUpdate appUpdate = appUpdateService.getLatestUpdate(appVersion, uid);
        if (appUpdate == null) {
            return getSuccessResponseVO(null);
        }
        AppUpdateVO updateVO = CopyTools.copy(appUpdate, AppUpdateVO.class);
        File file = new File(appConfig.getProjectFolder() + Constants.APP_UPDATE_FOLDER + appUpdate.getId() + Constants.APP_EXE_SUFFIX);
        updateVO.setSize(file.length());
        updateVO.setUpdateList(Arrays.asList(appUpdate.getUpdateDescArray()));
        String fileName = Constants.APP_NAME + appUpdate.getVersion() + Constants.APP_EXE_SUFFIX;
        updateVO.setFileName(fileName);
        return getSuccessResponseVO(updateVO);
    }

    @RequestMapping("/download")
    @GlobalInterceptor
    public void download(HttpServletResponse response, @NotNull Integer id) {
        AppUpdate appUpdate = appUpdateService.getAppUpdateById(id);
        File file = new File(appConfig.getProjectFolder() + Constants.APP_UPDATE_FOLDER + appUpdate.getId() + Constants.APP_EXE_SUFFIX);
        if (!file.exists()) {
            return;
        }
        response.setContentType("application/x-msdownload; charset=UTF-8");
        response.setHeader("Content-Disposition", "attachment;");
        response.setContentLengthLong(file.length());
        try (OutputStream out = response.getOutputStream(); FileInputStream in = new FileInputStream(file);) {
            byte[] byteData = new byte[1024];
            int len;
            while ((len = in.read(byteData)) != -1) {
                out.write(byteData, 0, len);
            }
            out.flush();
        } catch (Exception e) {
            logger.error("读取文件异常", e);
        }
    }
}
