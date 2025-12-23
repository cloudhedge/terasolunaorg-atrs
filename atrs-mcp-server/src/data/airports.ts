/**
 * Airport reference data from ATRS database
 * Source: atrs-initdb/src/sqls/integration-test-postgres/00200_insert_fixed_value.sql
 */

export interface Airport {
  code: string;
  name: string;
  nameEn: string;
}

export const airports: Airport[] = [
  // Major airports
  { code: 'HND', name: '東京(羽田)', nameEn: 'Tokyo (Haneda)' },
  { code: 'NRT', name: '東京(成田)', nameEn: 'Tokyo (Narita)' },
  { code: 'ITM', name: '大阪(伊丹)', nameEn: 'Osaka (Itami)' },
  { code: 'KIX', name: '大阪(関西)', nameEn: 'Osaka (Kansai)' },
  { code: 'UKB', name: '大阪(神戸)', nameEn: 'Osaka (Kobe)' },
  { code: 'SPK', name: '札幌(千歳)', nameEn: 'Sapporo (Chitose)' },
  { code: 'NGO', name: '名古屋(中部)', nameEn: 'Nagoya (Chubu)' },
  { code: 'FUK', name: '福岡', nameEn: 'Fukuoka' },
  { code: 'OKA', name: '沖縄', nameEn: 'Okinawa' },
  // Hokkaido
  { code: 'OKD', name: '札幌(丘珠)', nameEn: 'Sapporo (Okadama)' },
  { code: 'RIS', name: '利尻', nameEn: 'Rishiri' },
  { code: 'WKJ', name: '稚内', nameEn: 'Wakkanai' },
  { code: 'MBE', name: '紋別', nameEn: 'Monbetsu' },
  { code: 'MMB', name: '女満別', nameEn: 'Memanbetsu' },
  { code: 'AKJ', name: '旭川', nameEn: 'Asahikawa' },
  { code: 'SHB', name: '根室中標津', nameEn: 'Nakashibetsu' },
  { code: 'KUH', name: '釧路', nameEn: 'Kushiro' },
  { code: 'HKD', name: '函館', nameEn: 'Hakodate' },
  // Tohoku
  { code: 'ONJ', name: '大館能代', nameEn: 'Odate-Noshiro' },
  { code: 'AXT', name: '秋田', nameEn: 'Akita' },
  { code: 'SYO', name: '庄内', nameEn: 'Shonai' },
  { code: 'SDJ', name: '仙台', nameEn: 'Sendai' },
  { code: 'FKS', name: '福島', nameEn: 'Fukushima' },
  // Kanto/Chubu
  { code: 'OIM', name: '大島', nameEn: 'Oshima' },
  { code: 'MYE', name: '三宅島', nameEn: 'Miyakejima' },
  { code: 'HAC', name: '八丈島', nameEn: 'Hachijojima' },
  { code: 'KIJ', name: '新潟', nameEn: 'Niigata' },
  { code: 'TOY', name: '富山', nameEn: 'Toyama' },
  { code: 'KMQ', name: '小松', nameEn: 'Komatsu' },
  { code: 'NTQ', name: '能登', nameEn: 'Noto' },
  // Chugoku/Shikoku
  { code: 'OKJ', name: '岡山', nameEn: 'Okayama' },
  { code: 'HIJ', name: '広島', nameEn: 'Hiroshima' },
  { code: 'UBJ', name: '山口宇部', nameEn: 'Yamaguchi-Ube' },
  { code: 'TTJ', name: '鳥取', nameEn: 'Tottori' },
  { code: 'YGJ', name: '米子', nameEn: 'Yonago' },
  { code: 'IWJ', name: '石見', nameEn: 'Iwami' },
  { code: 'TAK', name: '高松', nameEn: 'Takamatsu' },
  { code: 'TKS', name: '徳島', nameEn: 'Tokushima' },
  { code: 'MYJ', name: '松山', nameEn: 'Matsuyama' },
  { code: 'KCZ', name: '高知', nameEn: 'Kochi' },
  // Kyushu
  { code: 'KKJ', name: '北九州', nameEn: 'Kitakyushu' },
  { code: 'HSG', name: '佐賀', nameEn: 'Saga' },
  { code: 'OIT', name: '大分', nameEn: 'Oita' },
  { code: 'KMJ', name: '熊本', nameEn: 'Kumamoto' },
  { code: 'NGS', name: '長崎', nameEn: 'Nagasaki' },
  { code: 'TSJ', name: '対馬', nameEn: 'Tsushima' },
  { code: 'FUJ', name: '五島福江', nameEn: 'Goto-Fukue' },
  { code: 'KMI', name: '宮崎', nameEn: 'Miyazaki' },
  { code: 'KOJ', name: '鹿児島', nameEn: 'Kagoshima' },
  // Okinawa
  { code: 'MMY', name: '宮古', nameEn: 'Miyako' },
  { code: 'ISG', name: '石垣', nameEn: 'Ishigaki' },
];

/**
 * Find airport by code or name (case-insensitive)
 */
export function findAirport(query: string): Airport | undefined {
  const q = query.toLowerCase();
  return airports.find(
    (a) =>
      a.code.toLowerCase() === q ||
      a.name.includes(query) ||
      a.nameEn.toLowerCase().includes(q)
  );
}

/**
 * Get airport code from city name (for user-friendly input)
 */
export function getAirportCode(cityOrCode: string): string | undefined {
  const airport = findAirport(cityOrCode);
  return airport?.code;
}
