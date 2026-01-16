/**
 * ATRS API Type Definitions
 * Based on Java classes in jp.co.ntt.atrs.api.* and jp.co.ntt.atrs.domain.model.*
 */

// ============ Enums ============
export type FlightType = 'RT' | 'OW'; // RT=Round-trip, OW=One-way
export type BoardingClassCd = 'N' | 'S'; // N=Normal, S=Special
export type Gender = 'F' | 'M'; // F=Female, M=Male
export type FareTypeCd =
  | 'OW'
  | 'RT'
  | 'RD1'
  | 'RD7'
  | 'ED'
  | 'LD'
  | 'GD'
  | 'SOW'
  | 'SRT'
  | 'SRD';

// ============ Request Types ============

/**
 * Flight search query parameters
 * Endpoint: GET /api/v1/flight
 */
export interface FlightSearchQuery {
  flightType: FlightType;
  depAirportCd: string; // 3-letter code
  arrAirportCd: string; // 3-letter code
  depDate: string; // format: yyyy/MM/dd
  boardingClassCd: BoardingClassCd;
}

/**
 * Passenger information for booking
 */
export interface PassengerResource {
  familyName: string; // Full-width Katakana, 1-10 chars
  givenName: string; // Full-width Katakana, 1-10 chars
  age: number;
  gender: Gender;
  membershipNumber?: string; // 10 digits
}

/**
 * Selected flight for booking
 */
export interface SelectFlightResource {
  depDate: string; // format: yyyy/MM/dd
  flightName: string; // e.g., "NTT001"
  boardingClassCd: BoardingClassCd;
  fareTypeCd: FareTypeCd;
}

/**
 * Ticket reservation request
 * Endpoint: POST /api/v1/ticket
 */
export interface TicketReserveRequest {
  // Contact/Representative info
  repFamilyName: string; // Full-width Katakana, 1-10 chars
  repGivenName: string; // Full-width Katakana, 1-10 chars
  repAge: number;
  repGender: Gender;
  repMembershipNumber?: string; // 10 digits
  repTel1: string; // 2-5 digits (area code)
  repTel2: string; // 1-4 digits
  repTel3: string; // exactly 4 digits
  repMail: string; // email format, max 256 chars

  // Flight info
  flightType: FlightType;
  selectFlightResourceList: SelectFlightResource[];
  passengerResourceList: PassengerResource[];
}

// ============ Response Types ============

/**
 * Fare type information in flight search response
 */
export interface FareTypeResource {
  fareTypeName: string; // e.g., "片道運賃"
  fare: string; // Price as string, e.g., "20600"
  vacantNum: number; // Available seats
}

/**
 * Flight information in search response
 */
export interface FlightResource {
  flightName: string; // e.g., "NTT001"
  depAirportName: string; // e.g., "東京(羽田)"
  arrAirportName: string; // e.g., "大阪(伊丹)"
  depTime: string; // e.g., "08:00"
  arrTime: string; // e.g., "09:15"
  depDate: string; // e.g., "2025/12/26"
  boardingClassCd: BoardingClassCd;
  fareTypes: Record<string, FareTypeResource>; // Key is FareTypeCd
}

/**
 * Ticket reservation response
 */
export interface TicketReserveResponse {
  reserveNo: string; // e.g., "ABC12345"
  paymentDate: string; // Payment deadline date
  totalFare: number; // Total fare in yen
}

/**
 * API error response
 */
export interface ApiError {
  code: string; // e.g., "e.ar.b1.2001"
  message: string | null;
}
