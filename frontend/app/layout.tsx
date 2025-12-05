import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Daxter - OpenTax Accountant Dashboard',
  description: 'Data Aggregation & AI Insights',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}