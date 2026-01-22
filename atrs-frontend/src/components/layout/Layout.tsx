/**
 * Layout wrapper component
 */
import type { ReactNode } from 'react';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <>
      <Header />
      <div className="container main-content">
        {children}
      </div>
      <Footer />
    </>
  );
}
