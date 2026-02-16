/**
 * ATRS MCP Server Constants
 * API configuration, airport codes, fare types, and reference data.
 */

export const API_BASE_URL =
  process.env.ATRS_API_URL || "http://localhost:8080/atrs/api/v1";

export const CHARACTER_LIMIT = 25000;

export const REQUEST_TIMEOUT = 30000;

/** All 50 Japanese airports in the ATRS system. */
export const AIRPORTS: ReadonlyArray<{
  code: string;
  name: string;
}> = [
  { code: "HND", name: "Haneda" },
  { code: "NRT", name: "Narita" },
  { code: "ITM", name: "Itami (Osaka)" },
  { code: "KIX", name: "Kansai" },
  { code: "SPK", name: "New Chitose (Sapporo)" },
  { code: "NGO", name: "Chubu Centrair (Nagoya)" },
  { code: "FUK", name: "Fukuoka" },
  { code: "OKA", name: "Naha (Okinawa)" },
  { code: "KOJ", name: "Kagoshima" },
  { code: "KMI", name: "Miyazaki" },
  { code: "OIT", name: "Oita" },
  { code: "KMJ", name: "Kumamoto" },
  { code: "NGS", name: "Nagasaki" },
  { code: "HSG", name: "Saga" },
  { code: "SDJ", name: "Sendai" },
  { code: "KIJ", name: "Niigata" },
  { code: "AOJ", name: "Aomori" },
  { code: "AXT", name: "Akita" },
  { code: "HNA", name: "Hanamaki (Iwate)" },
  { code: "GAJ", name: "Yamagata" },
  { code: "HIJ", name: "Hiroshima" },
  { code: "UBJ", name: "Yamaguchi Ube" },
  { code: "OKJ", name: "Okayama" },
  { code: "IZO", name: "Izumo" },
  { code: "YGJ", name: "Yonago" },
  { code: "TKS", name: "Tokushima" },
  { code: "TAK", name: "Takamatsu" },
  { code: "MYJ", name: "Matsuyama" },
  { code: "KCZ", name: "Kochi" },
  { code: "TOY", name: "Toyama" },
  { code: "KMQ", name: "Komatsu (Ishikawa)" },
  { code: "MMJ", name: "Matsumoto" },
  { code: "FSZ", name: "Shizuoka" },
  { code: "SHM", name: "Nanki Shirahama" },
  { code: "ISG", name: "Ishigaki" },
  { code: "MMY", name: "Miyako" },
  { code: "ASJ", name: "Amami" },
  { code: "TKN", name: "Tokunoshima" },
  { code: "OKE", name: "Okinoerabu" },
  { code: "RNJ", name: "Yoron" },
  { code: "KKJ", name: "Kitakyushu" },
  { code: "TNE", name: "Tanegashima" },
  { code: "KUM", name: "Yakushima" },
  { code: "OBO", name: "Obihiro" },
  { code: "AKJ", name: "Asahikawa" },
  { code: "MMB", name: "Memanbetsu" },
  { code: "KUH", name: "Kushiro" },
  { code: "HKD", name: "Hakodate" },
  { code: "WKJ", name: "Wakkanai" },
  { code: "MBE", name: "Monbetsu" },
];

/** Valid airport codes set for quick validation. */
export const AIRPORT_CODES = new Set(AIRPORTS.map((a) => a.code));

/** All 10 fare types in the ATRS system. */
export const FARE_TYPES: ReadonlyArray<{
  code: string;
  name: string;
  discountRate: number;
  bookingWindowDays: string;
  minPassengers: number;
  notes: string;
}> = [
  {
    code: "OW",
    name: "One-way",
    discountRate: 0,
    bookingWindowDays: "90-0",
    minPassengers: 1,
    notes: "Standard one-way fare",
  },
  {
    code: "RT",
    name: "Round-trip",
    discountRate: 5,
    bookingWindowDays: "90-0",
    minPassengers: 1,
    notes: "5% discount for round-trip",
  },
  {
    code: "RD1",
    name: "Advance-1 day",
    discountRate: 10,
    bookingWindowDays: "60-1",
    minPassengers: 1,
    notes: "Book at least 1 day ahead",
  },
  {
    code: "RD7",
    name: "Advance-7 days",
    discountRate: 20,
    bookingWindowDays: "60-7",
    minPassengers: 1,
    notes: "Book at least 7 days ahead",
  },
  {
    code: "ED",
    name: "Early discount",
    discountRate: 30,
    bookingWindowDays: "60-30",
    minPassengers: 1,
    notes: "Book at least 30 days ahead",
  },
  {
    code: "LD",
    name: "Ladies discount",
    discountRate: 30,
    bookingWindowDays: "60-1",
    minPassengers: 1,
    notes: "Women only, 30% discount",
  },
  {
    code: "GD",
    name: "Group discount",
    discountRate: 30,
    bookingWindowDays: "60-1",
    minPassengers: 3,
    notes: "Requires 3+ passengers",
  },
  {
    code: "SOW",
    name: "Special one-way",
    discountRate: 0,
    bookingWindowDays: "90-0",
    minPassengers: 1,
    notes: "Special class one-way",
  },
  {
    code: "SRT",
    name: "Special round-trip",
    discountRate: 5,
    bookingWindowDays: "90-0",
    minPassengers: 1,
    notes: "Special class round-trip",
  },
  {
    code: "SRD",
    name: "Special advance",
    discountRate: 10,
    bookingWindowDays: "60-1",
    minPassengers: 1,
    notes: "Special class advance booking",
  },
];

/** Boarding class definitions. */
export const BOARDING_CLASSES = [
  { code: "N", name: "Normal", extraCharge: 0 },
  { code: "S", name: "Special", extraCharge: 5000 },
] as const;
