import "./styles.css";

export const metadata = {
  title: "Laraloop Studio",
  description: "Brand DNA extraction and campaign studio"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
