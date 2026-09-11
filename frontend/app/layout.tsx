import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata = {
  title: 'NOVA — Your autonomous layer over Amazon',
  description: 'NOVA learns how your household shops, predicts what you need, prepares your Amazon shopping plan, watches prices, and acts within rules you define.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased text-neutral-900">
        <Navbar />
        {children}
      </body>
    </html>
  );
}
