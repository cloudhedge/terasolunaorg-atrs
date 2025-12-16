/*
 * Copyright(c) 2024 NTT Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
 * either express or implied. See the License for the specific language
 * governing permissions and limitations under the License.
 */
package jp.co.ntt.atrs.app.common;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

/**
 * Swagger UI controller.
 */
@Controller
public class SwaggerController {

    private static final String SWAGGER_HTML = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>ATRS API - Swagger UI</title>
            <link rel="stylesheet" type="text/css" href="/atrs/webjars/swagger-ui/5.18.2/swagger-ui.css">
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="/atrs/webjars/swagger-ui/5.18.2/swagger-ui-bundle.js"></script>
            <script src="/atrs/webjars/swagger-ui/5.18.2/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {
                    SwaggerUIBundle({
                        url: "/atrs/api/v1/v3/api-docs",
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        layout: "StandaloneLayout"
                    });
                };
            </script>
        </body>
        </html>
        """;

    @GetMapping(value = "/swagger-ui.html", produces = "text/html")
    @ResponseBody
    public String swaggerUi() {
        return SWAGGER_HTML;
    }
}
