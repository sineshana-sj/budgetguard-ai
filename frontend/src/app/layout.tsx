import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'BudgetGuard AI — Strands Decider Intelligent Routing Dashboard',
  description: 'Enterprise AI cost-optimization and model routing platform powered by Strands Decider 2B & Amazon Bedrock',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
