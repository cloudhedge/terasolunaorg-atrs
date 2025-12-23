/**
 * ATRS API Type Definitions
 * Based on ATRS REST API contracts
 */

// ============ Enums ============

export type FlightType = 'RT' | 'OW';
export type BoardingClassCd = 'N' | 'S';
export type Gender = 'F' | 'M';
export type FareTypeCd = 'OW' | 'RT' | 'RD1' | 'RD7' | 'ED' | 'LD' | 'GD' | 'SOW' | 'SRT' | 'SRD';

// ============ Flight Search ============

/** GET /flight query parameters */
export interface FlightSearchQuery {
  flightType: FlightType;
  depAirportCd: string;
  arrAirportCd: string;
  depDate: string; // yyyy/MM/dd
  boardingClassCd: BoardingClassCd;
}

/** Fare type information in flight response */
export interface FareTypeResource {
  fareTypeName: string;
  fare: string;
  vacantNum: number;
}

/** Flight search response item */
export interface FlightResource {
  flightName: string;
  depAirportName: string;
  arrAirportName: string;
  depTime: string;
  arrTime: string;
  depDate: string;
  boardingClassCd: BoardingClassCd;
  fareTypes: Record<string, FareTypeResource>;
}

// ============ Ticket Reservation ============

/** Selected flight for booking */
export interface SelectFlightResource {
  depDate: string; // yyyy/MM/dd
  flightName: string;
  boardingClassCd: BoardingClassCd;
  fareTypeCd: FareTypeCd;
}

/** Passenger information */
export interface PassengerResource {
  familyName: string;
  givenName: string;
  age: number;
  gender: Gender;
  membershipNumber?: string;
}

/** POST /ticket request body */
export interface TicketReserveRequest {
  repFamilyName: string;
  repGivenName: string;
  repAge: number;
  repGender: Gender;
  repMembershipNumber?: string;
  repTel1: string;
  repTel2: string;
  repTel3: string;
  repMail: string;
  flightType: FlightType;
  selectFlightResourceList: SelectFlightResource[];
  passengerResourceList: PassengerResource[];
}

/** POST /ticket response */
export interface TicketReserveResponse {
  reserveNo: string;
  paymentDate: string;
  totalFare: number;
  repFamilyName: string;
  repGivenName: string;
  repAge: number;
  repGender: Gender;
  repTel1: string;
  repTel2: string;
  repTel3: string;
  repMail: string;
  flightType: FlightType;
  selectFlightResourceList: SelectFlightResource[];
  passengerResourceList: PassengerResource[];
}

// ============ Error Response ============

export interface ErrorResult {
  messages: string[];
}
