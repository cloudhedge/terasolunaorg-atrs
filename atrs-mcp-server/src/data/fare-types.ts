/**
 * Fare type reference data from ATRS database
 * Source: atrs-initdb/src/sqls/integration-test-postgres/00200_insert_fixed_value.sql
 */

export interface FareType {
  code: string;
  name: string;
  nameEn: string;
  discountPercent: number;
  minDaysBeforeDeparture: number;
  minPassengers: number;
  description: string;
}

export const fareTypes: FareType[] = [
  {
    code: 'OW',
    name: '片道運賃',
    nameEn: 'One-way',
    discountPercent: 0,
    minDaysBeforeDeparture: 0,
    minPassengers: 1,
    description: 'Standard one-way fare, no discount',
  },
  {
    code: 'RT',
    name: '往復運賃',
    nameEn: 'Round-trip',
    discountPercent: 5,
    minDaysBeforeDeparture: 0,
    minPassengers: 1,
    description: '5% discount for round-trip booking',
  },
  {
    code: 'RD1',
    name: '予約割1',
    nameEn: 'Advance 1-day',
    discountPercent: 10,
    minDaysBeforeDeparture: 1,
    minPassengers: 1,
    description: '10% discount when booking 1+ days in advance',
  },
  {
    code: 'RD7',
    name: '予約割7',
    nameEn: 'Advance 7-day',
    discountPercent: 20,
    minDaysBeforeDeparture: 7,
    minPassengers: 1,
    description: '20% discount when booking 7+ days in advance',
  },
  {
    code: 'ED',
    name: '早期割',
    nameEn: 'Early Bird',
    discountPercent: 30,
    minDaysBeforeDeparture: 30,
    minPassengers: 1,
    description: '30% discount when booking 30+ days in advance',
  },
  {
    code: 'LD',
    name: 'レディース割',
    nameEn: 'Ladies Discount',
    discountPercent: 30,
    minDaysBeforeDeparture: 1,
    minPassengers: 1,
    description: '30% discount for female passengers',
  },
  {
    code: 'GD',
    name: 'グループ割',
    nameEn: 'Group Discount',
    discountPercent: 30,
    minDaysBeforeDeparture: 1,
    minPassengers: 3,
    description: '30% discount for groups of 3+ passengers',
  },
  {
    code: 'SOW',
    name: '特別片道運賃',
    nameEn: 'Special One-way',
    discountPercent: 0,
    minDaysBeforeDeparture: 0,
    minPassengers: 1,
    description: 'Special class one-way fare',
  },
  {
    code: 'SRT',
    name: '特別往復運賃',
    nameEn: 'Special Round-trip',
    discountPercent: 5,
    minDaysBeforeDeparture: 0,
    minPassengers: 1,
    description: 'Special class round-trip with 5% discount',
  },
  {
    code: 'SRD',
    name: '特別予約割',
    nameEn: 'Special Advance',
    discountPercent: 10,
    minDaysBeforeDeparture: 1,
    minPassengers: 1,
    description: 'Special class advance booking with 10% discount',
  },
];

/**
 * Find fare type by code
 */
export function findFareType(code: string): FareType | undefined {
  return fareTypes.find((f) => f.code.toUpperCase() === code.toUpperCase());
}
