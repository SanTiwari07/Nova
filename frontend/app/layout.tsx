import './globals.css';
import Header from '@/components/Header';
import FloatingCopilotDrawer from '@/components/FloatingCopilotDrawer';

export const metadata = {
  title: 'NOVA - Household Autopilot & Intelligence',
  description: 'NOVA takes care of everyday household decisions for you - managing inventory, predicting needs, and acting within your rules.',
  icons: {
    icon: '/logo.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased text-neutral-900 bg-[#FAFAF8]">
        <Header />
        {children}
        <FloatingCopilotDrawer />
      </body>
    </html>
  );
}
