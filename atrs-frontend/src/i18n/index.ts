/**
 * i18n configuration with react-i18next
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translation files
import common from '../../public/locales/ja/common.json';
import auth from '../../public/locales/ja/auth.json';
import flight from '../../public/locales/ja/flight.json';
import reserve from '../../public/locales/ja/reserve.json';
import errors from '../../public/locales/ja/errors.json';

i18n.use(initReactI18next).init({
  resources: {
    ja: {
      common,
      auth,
      flight,
      reserve,
      errors,
    },
  },
  lng: 'ja',
  fallbackLng: 'ja',
  ns: ['common', 'auth', 'flight', 'reserve', 'errors'],
  defaultNS: 'common',
  interpolation: {
    escapeValue: false, // React already escapes
  },
});

export default i18n;
