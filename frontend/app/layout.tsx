import './globals.css';
import Header from '@/components/Header';

export const metadata = {
  title: 'NOVA — Household Shopping & Autopilot',
  description: 'NOVA is your household commerce companion. Shop groceries, household supplies, and personal care while NOVA intelligently manages your household inventory and autopilot decisions.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased text-neutral-900 bg-[#f3f3f3]">
        <Header />
        {children}
      </body>
    </html>
  );
}
