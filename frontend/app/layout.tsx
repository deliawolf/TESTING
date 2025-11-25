import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { GatewayControl } from "@/components/gateway-control"
import { RefreshButton } from "@/components/refresh-button"
import { BackendHealthCheck } from "@/components/backend-health-check"

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Network Automation Tool",
  description: "Premium Network Automation Interface",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SidebarProvider>
          <AppSidebar />
          <main className="w-full">
            <div className="border-b bg-background">
              <div className="flex h-14 items-center justify-between px-4">
                <SidebarTrigger />
                <div className="flex items-center gap-2">
                  <RefreshButton />
                  <GatewayControl />
                </div>
              </div>
            </div>
            <div className="p-4">
              <BackendHealthCheck />
              {children}
            </div>
          </main>
        </SidebarProvider>
      </body>
    </html>
  );
}
