/**
 * Footer component - migrated from footer.jsp
 */
import { useTranslation } from 'react-i18next';

export default function Footer() {
  const { t } = useTranslation();

  return (
    <footer id="footer">
      <div className="container">
        <span>{t('footer.copyright')}</span>
      </div>
    </footer>
  );
}
