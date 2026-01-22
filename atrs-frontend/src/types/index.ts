/**
 * TypeScript types for the ATRS application
 */

// Enums matching Python backend
export type BoardingClassCd = 'N' | 'S';
export type FareTypeCd = 'OW' | 'RT' | 'RP' | 'SP1' | 'SP2' | 'ED' | 'LD';
export type FlightType = 'OW' | 'RT';
export type Gender = 'M' | 'F';

// Auth types
export interface User {
  membershipNumber: string;
  name: string;
  email?: string;
}

export interface LoginRequest {
  username: string; // membership_number
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  membership_number: string;
}

// Flight types
export interface FareType {
  fare_type_cd: FareTypeCd;
  fare_type_name: string;
  fare: number;
  vacant_num: number;
}

export interface Flight {
  departure_date: string;
  flight_name: string;
  departure_time: string;
  arrival_time: string;
  departure_airport_name: string;
  arrival_airport_name: string;
  boarding_class_cd: BoardingClassCd;
  fare_types: FareType[];
}

export interface FlightSearchCriteria {
  departureDate: string;
  depAirportCd: string;
  arrAirportCd: string;
  boardingClassCd: BoardingClassCd;
  flightType: FlightType;
}

// Flight selection for reservation
export interface FlightSelection {
  departure_date: string;
  flight_name: string;
  boarding_class_cd: BoardingClassCd;
  fare_type_cd: FareTypeCd;
  // Display info
  departure_time?: string;
  arrival_time?: string;
  departure_airport_name?: string;
  arrival_airport_name?: string;
  fare?: number;
  fare_type_name?: string;
}

// Reservation types
export interface Passenger {
  family_name: string;
  given_name: string;
  age: number;
  gender: Gender;
  customer_no?: string;
}

export interface ReservationRequest {
  flights: FlightSelection[];
  passengers: Passenger[];
  rep_family_name: string;
  rep_given_name: string;
  rep_age: number;
  rep_gender: Gender;
  rep_tel: string;
  rep_mail: string;
  rep_customer_no?: string;
}

export interface ReservationResponse {
  reserve_no: string;
  total_fare: number;
  message: string;
}

// Airport reference data
export interface Airport {
  code: string;
  name: string;
}

export const AIRPORTS: Airport[] = [
  { code: 'HND', name: '羽田' },
  { code: 'ITM', name: '伊丹' },
  { code: 'SPK', name: '新千歳' },
  { code: 'FUK', name: '福岡' },
  { code: 'OKA', name: '沖縄' },
  { code: 'NGO', name: '中部国際' },
  { code: 'KIX', name: '関西国際' },
  { code: 'SDJ', name: '仙台' },
  { code: 'HIJ', name: '広島' },
  { code: 'KOJ', name: '鹿児島' },
];

// Boarding class reference
export const BOARDING_CLASSES: { code: BoardingClassCd; name: string }[] = [
  { code: 'N', name: '普通席' },
  { code: 'S', name: '特別席' },
];

// Flight type reference
export const FLIGHT_TYPES: { code: FlightType; name: string }[] = [
  { code: 'RT', name: '往復' },
  { code: 'OW', name: '片道' },
];

// Gender reference
export const GENDERS: { code: Gender; name: string }[] = [
  { code: 'M', name: '男性' },
  { code: 'F', name: '女性' },
];
