/**
 * Fare type reference data sourced from:
 * JavaConfig-JSP/atrs/atrs-initdb/src/sqls/integration-test-postgres/00200_insert_fixed_value.sql
 */
export interface FareType {
  code: string;
  name: string; // Japanese name from DB
  nameEn: string; // English name for AI
  discountRate: number; // Percentage discount
  rsrvAvailableStartDayNum: number; // Days before departure to start booking
  rsrvAvailableEndDayNum: number; // Days before departure to end booking
  passengerMinNum: number; // Minimum passengers required
  displayOrder: number;
  seatClass: 'N' | 'S'; // N=Normal, S=Special
}

export const fareTypes: FareType[] = [
  // Normal seat fare types (displayOrder 1-7)
  {
    code: 'OW',
    name: '片道運賃',
    nameEn: 'One-way',
    discountRate: 0,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 1,
    seatClass: 'N',
  },
  {
    code: 'RT',
    name: '往復運賃',
    nameEn: 'Round-trip',
    discountRate: 5,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 2,
    seatClass: 'N',
  },
  {
    code: 'RD1',
    name: '予約割1',
    nameEn: 'Advance 1-day',
    discountRate: 10,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 1,
    displayOrder: 3,
    seatClass: 'N',
  },
  {
    code: 'RD7',
    name: '予約割7',
    nameEn: 'Advance 7-day',
    discountRate: 20,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 7,
    passengerMinNum: 1,
    displayOrder: 4,
    seatClass: 'N',
  },
  {
    code: 'ED',
    name: '早期割',
    nameEn: 'Early Bird',
    discountRate: 30,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 30,
    passengerMinNum: 1,
    displayOrder: 5,
    seatClass: 'N',
  },
  {
    code: 'LD',
    name: 'レディース割',
    nameEn: 'Ladies Discount',
    discountRate: 30,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 1,
    displayOrder: 6,
    seatClass: 'N',
  },
  {
    code: 'GD',
    name: 'グループ割',
    nameEn: 'Group Discount',
    discountRate: 30,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 3,
    displayOrder: 7,
    seatClass: 'N',
  },
  // Special seat fare types (displayOrder 100+)
  {
    code: 'SOW',
    name: '特別片道運賃',
    nameEn: 'Special One-way',
    discountRate: 0,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 100,
    seatClass: 'S',
  },
  {
    code: 'SRT',
    name: '特別往復運賃',
    nameEn: 'Special Round-trip',
    discountRate: 5,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 101,
    seatClass: 'S',
  },
  {
    code: 'SRD',
    name: '特別予約割',
    nameEn: 'Special Advance',
    discountRate: 10,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 1,
    displayOrder: 102,
    seatClass: 'S',
  },
];

/**
 * Find fare type by code or name
 */
export function findFareType(query: string): FareType | undefined {
  const q = query.toLowerCase().trim();
  return fareTypes.find(
    (f) =>
      f.code.toLowerCase() === q ||
      f.nameEn.toLowerCase().includes(q) ||
      f.name.includes(query)
  );
}
