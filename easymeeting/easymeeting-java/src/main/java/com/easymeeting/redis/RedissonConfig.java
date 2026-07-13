package com.easymeeting.redis;

import com.easymeeting.entity.constants.Constants;
import io.lettuce.core.RedisConnectionException;
import org.redisson.Redisson;
import org.redisson.api.RedissonClient;
import org.redisson.codec.JsonJacksonCodec;
import org.redisson.config.Config;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = Constants.MESSAGEING_HANDLE_CHANNEL_KEY, havingValue = Constants.MESSAGEING_HANDLE_CHANNEL_REDIS)
public class RedissonConfig {
    private static final Logger logger = LoggerFactory.getLogger(RedisConfig.class);

    @Value("${spring.redis.host:}")
    private String redisHost;

    @Value("${spring.redis.port:}")
    private Integer redisPort;

    @Bean(name = "redissonClient", destroyMethod = "shutdown")
    public RedissonClient redissonClient() {
        try {
            // 创建配置 指定redis地址及节点信息
            Config config = new Config();
            // 用 JsonJacksonCodec 替代默认的 FstCodec，避免 FST 在 Java 21 上反射
            // JDK 内部字段（java.lang.String.value / java.math.BigDecimal 等）触发模块访问异常
            config.setCodec(new JsonJacksonCodec());
            config.useSingleServer().setAddress("redis://" + redisHost + ":" + redisPort);
            // 根据config创建出RedissonClient实例
            RedissonClient redissonClient = Redisson.create(config);
            return redissonClient;
        } catch (RedisConnectionException e) {
            logger.error("redis配置错误，请检查redis配置");
        }
        return null;
    }
}
