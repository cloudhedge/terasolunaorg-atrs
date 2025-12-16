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
package jp.co.ntt.atrs.api.openapi;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.springframework.http.MediaType;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.servlet.http.HttpServletResponse;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.Operation;
import io.swagger.v3.oas.models.PathItem;
import io.swagger.v3.oas.models.Paths;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.media.ArraySchema;
import io.swagger.v3.oas.models.media.BooleanSchema;
import io.swagger.v3.oas.models.media.Content;
import io.swagger.v3.oas.models.media.IntegerSchema;
import io.swagger.v3.oas.models.media.ObjectSchema;
import io.swagger.v3.oas.models.media.Schema;
import io.swagger.v3.oas.models.media.StringSchema;
import io.swagger.v3.oas.models.parameters.Parameter;
import io.swagger.v3.oas.models.parameters.RequestBody;
import io.swagger.v3.oas.models.responses.ApiResponse;
import io.swagger.v3.oas.models.responses.ApiResponses;
import io.swagger.v3.oas.models.servers.Server;

/**
 * OpenAPI specification controller.
 */
@Controller
@RequestMapping("v3/api-docs")
public class OpenApiController {

    private final ObjectMapper objectMapper;

    public OpenApiController() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    }

    @GetMapping
    public void getOpenApiSpec(HttpServletResponse response) throws IOException {
        OpenAPI openAPI = new OpenAPI();

        // Info
        openAPI.info(new Info()
            .title("ATRS - Airline Ticket Reservation System API")
            .description("API for flight search, ticket booking, and member management")
            .version("1.0.0"));

        // Server
        openAPI.servers(List.of(new Server().url("/atrs/api/v1")));

        // Paths
        Paths paths = new Paths();

        // GET /flight - Search flights
        paths.addPathItem("/flight", new PathItem()
            .get(new Operation()
                .summary("Search available flights")
                .description("Find flights by route, date, and boarding class")
                .operationId("searchFlights")
                .addParametersItem(new Parameter()
                    .name("flightType")
                    .in("query")
                    .required(true)
                    .description("Flight type: OW (One Way) or RT (Round Trip)")
                    .schema(new StringSchema()._enum(Arrays.asList("OW", "RT"))))
                .addParametersItem(new Parameter()
                    .name("depAirportCd")
                    .in("query")
                    .required(true)
                    .description("Departure airport code")
                    .example("HND")
                    .schema(new StringSchema()))
                .addParametersItem(new Parameter()
                    .name("arrAirportCd")
                    .in("query")
                    .required(true)
                    .description("Arrival airport code")
                    .example("KIX")
                    .schema(new StringSchema()))
                .addParametersItem(new Parameter()
                    .name("depDate")
                    .in("query")
                    .required(true)
                    .description("Departure date (yyyy/MM/dd)")
                    .example("2025/01/15")
                    .schema(new StringSchema().format("date")))
                .addParametersItem(new Parameter()
                    .name("boardingClassCd")
                    .in("query")
                    .required(true)
                    .description("Boarding class: N (Normal), S (Special)")
                    .schema(new StringSchema()._enum(Arrays.asList("N", "S"))))
                .responses(new ApiResponses()
                    .addApiResponse("200", new ApiResponse()
                        .description("List of available flights")
                        .content(new Content()
                            .addMediaType(MediaType.APPLICATION_JSON_VALUE,
                                new io.swagger.v3.oas.models.media.MediaType()
                                    .schema(new ArraySchema().items(flightResourceSchema())))))
                    .addApiResponse("400", new ApiResponse()
                        .description("Invalid search criteria")))));

        // POST /ticket - Reserve ticket
        paths.addPathItem("/ticket", new PathItem()
            .post(new Operation()
                .summary("Reserve a ticket")
                .description("Create a new ticket reservation")
                .operationId("reserveTicket")
                .requestBody(new RequestBody()
                    .required(true)
                    .content(new Content()
                        .addMediaType(MediaType.APPLICATION_JSON_VALUE,
                            new io.swagger.v3.oas.models.media.MediaType()
                                .schema(ticketReserveRequestSchema()))))
                .responses(new ApiResponses()
                    .addApiResponse("201", new ApiResponse()
                        .description("Ticket reserved successfully")
                        .content(new Content()
                            .addMediaType(MediaType.APPLICATION_JSON_VALUE,
                                new io.swagger.v3.oas.models.media.MediaType()
                                    .schema(ticketReserveResponseSchema()))))
                    .addApiResponse("400", new ApiResponse()
                        .description("Invalid reservation data")))));

        // GET /ticket/check - Check reservation
        paths.addPathItem("/ticket/check", new PathItem()
            .get(new Operation()
                .summary("Check reservation exists")
                .description("Verify if a reservation exists by reservation number")
                .operationId("checkReservation")
                .addParametersItem(new Parameter()
                    .name("reserveNo")
                    .in("query")
                    .required(true)
                    .description("Reservation number")
                    .schema(new StringSchema()))
                .responses(new ApiResponses()
                    .addApiResponse("200", new ApiResponse()
                        .description("Reservation check result")
                        .content(new Content()
                            .addMediaType(MediaType.APPLICATION_JSON_VALUE,
                                new io.swagger.v3.oas.models.media.MediaType()
                                    .schema(new BooleanSchema())))))));

        openAPI.paths(paths);

        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");
        objectMapper.writeValue(response.getWriter(), openAPI);
    }

    @SuppressWarnings("rawtypes")
    private Schema flightResourceSchema() {
        return new ObjectSchema()
            .addProperty("flightName", new StringSchema().description("Flight name").example("NH001"))
            .addProperty("depAirportCd", new StringSchema().description("Departure airport code"))
            .addProperty("arrAirportCd", new StringSchema().description("Arrival airport code"))
            .addProperty("depTime", new StringSchema().description("Departure time"))
            .addProperty("arrTime", new StringSchema().description("Arrival time"))
            .addProperty("boardingClassCd", new StringSchema().description("Boarding class"))
            .addProperty("fareTypeCd", new StringSchema().description("Fare type code"))
            .addProperty("fare", new IntegerSchema().description("Fare amount"))
            .addProperty("vacantNum", new IntegerSchema().description("Number of vacant seats"));
    }

    @SuppressWarnings("rawtypes")
    private Schema ticketReserveRequestSchema() {
        return new ObjectSchema()
            .addProperty("selectFlightResourceList", new ArraySchema()
                .items(new ObjectSchema()
                    .addProperty("flightName", new StringSchema())
                    .addProperty("depDate", new StringSchema())
                    .addProperty("boardingClassCd", new StringSchema())
                    .addProperty("fareTypeCd", new StringSchema())))
            .addProperty("passengerResourceList", new ArraySchema()
                .items(new ObjectSchema()
                    .addProperty("familyName", new StringSchema())
                    .addProperty("givenName", new StringSchema())
                    .addProperty("age", new IntegerSchema())
                    .addProperty("gender", new StringSchema())));
    }

    @SuppressWarnings("rawtypes")
    private Schema ticketReserveResponseSchema() {
        return new ObjectSchema()
            .addProperty("reserveNo", new StringSchema().description("Reservation number"))
            .addProperty("totalFare", new IntegerSchema().description("Total fare"));
    }
}
