
package com.bantu.sense.spine_engine.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate() {
        // We use the 'Factory' to set the timeout limits manually
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();

        factory.setConnectTimeout(3000); // 3 seconds to find Python
        factory.setReadTimeout(5000);    // 5 seconds to get an answer

        return new RestTemplate(factory);
    }
}