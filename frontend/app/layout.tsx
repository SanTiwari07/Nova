import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata = {
  title: 'NOVA',
  description: 'The intelligence layer for everyday life.',
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
