/**
 * Airport reference data sourced from:
 * JavaConfig-JSP/atrs/atrs-initdb/src/sqls/integration-test-postgres/00200_insert_fixed_value.sql
 */
export interface Airport {
  code: string;
  name: string; // Japanese name from DB
  nameEn: string; // English name for AI
  displayOrder: number;
}

export const airports: Airport[] = [
  // Major airports (displayOrder 1-9)
  { code: 'HND', name: '東京(羽田)', nameEn: 'Tokyo Haneda', displayOrder: 1 },
  { code: 'NRT', name: '東京(成田)', nameEn: 'Tokyo Narita', displayOrder: 2 },
  { code: 'ITM', name: '大阪(伊丹)', nameEn: 'Osaka Itami', displayOrder: 3 },
  { code: 'KIX', name: '大阪(関西)', nameEn: 'Osaka Kansai', displayOrder: 4 },
  { code: 'UKB', name: '大阪(神戸)', nameEn: 'Osaka Kobe', displayOrder: 5 },
  { code: 'SPK', name: '札幌(千歳)', nameEn: 'Sapporo Chitose', displayOrder: 6 },
  { code: 'NGO', name: '名古屋(中部)', nameEn: 'Nagoya Chubu', displayOrder: 7 },
  { code: 'FUK', name: '福岡', nameEn: 'Fukuoka', displayOrder: 8 },
  { code: 'OKA', name: '沖縄', nameEn: 'Okinawa', displayOrder: 9 },

  // Regional airports (displayOrder 100+)
  { code: 'OKD', name: '札幌(丘珠)', nameEn: 'Sapporo Okadama', displayOrder: 100 },
  { code: 'RIS', name: '利尻', nameEn: 'Rishiri', displayOrder: 101 },
  { code: 'WKJ', name: '稚内', nameEn: 'Wakkanai', displayOrder: 102 },
  { code: 'MBE', name: 'オホーツク紋別', nameEn: 'Okhotsk Monbetsu', displayOrder: 103 },
  { code: 'MMB', name: '女満別', nameEn: 'Memambetsu', displayOrder: 104 },
  { code: 'AKJ', name: '旭川', nameEn: 'Asahikawa', displayOrder: 105 },
  { code: 'SHB', name: '根室中標津', nameEn: 'Nemuro Nakashibetsu', displayOrder: 106 },
  { code: 'KUH', name: '釧路', nameEn: 'Kushiro', displayOrder: 107 },
  { code: 'HKD', name: '函館', nameEn: 'Hakodate', displayOrder: 108 },
  { code: 'ONJ', name: '大館能代', nameEn: 'Odate Noshiro', displayOrder: 109 },
  { code: 'AXT', name: '秋田', nameEn: 'Akita', displayOrder: 110 },
  { code: 'SYO', name: '庄内', nameEn: 'Shonai', displayOrder: 111 },
  { code: 'SDJ', name: '仙台', nameEn: 'Sendai', displayOrder: 112 },
  { code: 'FKS', name: '福島', nameEn: 'Fukushima', displayOrder: 113 },
  { code: 'OIM', name: '大島', nameEn: 'Oshima', displayOrder: 114 },
  { code: 'MYE', name: '三宅島', nameEn: 'Miyakejima', displayOrder: 115 },
  { code: 'HAC', name: '八丈島', nameEn: 'Hachijojima', displayOrder: 116 },
  { code: 'KIJ', name: '新潟', nameEn: 'Niigata', displayOrder: 117 },
  { code: 'TOY', name: '富山', nameEn: 'Toyama', displayOrder: 118 },
  { code: 'KMQ', name: '小松', nameEn: 'Komatsu', displayOrder: 119 },
  { code: 'NTQ', name: '能登', nameEn: 'Noto', displayOrder: 120 },
  { code: 'OKJ', name: '岡山', nameEn: 'Okayama', displayOrder: 121 },
  { code: 'HIJ', name: '広島', nameEn: 'Hiroshima', displayOrder: 122 },
  { code: 'UBJ', name: '山口宇部', nameEn: 'Yamaguchi Ube', displayOrder: 123 },
  { code: 'TTJ', name: '鳥取', nameEn: 'Tottori', displayOrder: 124 },
  { code: 'YGJ', name: '米子', nameEn: 'Yonago', displayOrder: 125 },
  { code: 'IWJ', name: '萩・石見', nameEn: 'Hagi Iwami', displayOrder: 126 },
  { code: 'TAK', name: '高松', nameEn: 'Takamatsu', displayOrder: 127 },
  { code: 'TKS', name: '徳島', nameEn: 'Tokushima', displayOrder: 128 },
  { code: 'MYJ', name: '松山', nameEn: 'Matsuyama', displayOrder: 129 },
  { code: 'KCZ', name: '高知', nameEn: 'Kochi', displayOrder: 130 },
  { code: 'KKJ', name: '北九州', nameEn: 'Kitakyushu', displayOrder: 131 },
  { code: 'HSG', name: '佐賀', nameEn: 'Saga', displayOrder: 132 },
  { code: 'OIT', name: '大分', nameEn: 'Oita', displayOrder: 133 },
  { code: 'KMJ', name: '熊本', nameEn: 'Kumamoto', displayOrder: 134 },
  { code: 'NGS', name: '長崎', nameEn: 'Nagasaki', displayOrder: 135 },
  { code: 'TSJ', name: '対馬', nameEn: 'Tsushima', displayOrder: 136 },
  { code: 'FUJ', name: '五島福江', nameEn: 'Goto Fukue', displayOrder: 137 },
  { code: 'KMI', name: '宮崎', nameEn: 'Miyazaki', displayOrder: 138 },
  { code: 'KOJ', name: '鹿児島', nameEn: 'Kagoshima', displayOrder: 139 },
  { code: 'MMY', name: '宮古', nameEn: 'Miyako', displayOrder: 140 },
  { code: 'ISG', name: '石垣', nameEn: 'Ishigaki', displayOrder: 141 },
];

/**
 * Find airport by code or name (English or Japanese)
 */
export function findAirport(query: string): Airport | undefined {
  const q = query.toLowerCase().trim();
  return airports.find(
    (a) =>
      a.code.toLowerCase() === q ||
      a.nameEn.toLowerCase().includes(q) ||
      a.name.includes(query)
  );
}

/**
 * Get airport code from city name or code
 */
export function getAirportCode(cityOrCode: string): string | undefined {
  const airport = findAirport(cityOrCode);
  return airport?.code;
}
