import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { SupplierOnboarding } from "./pages/SupplierOnboarding";
import { Catalog } from "./pages/Catalog";
import { CoffeeDetail } from "./pages/CoffeeDetail";
import { InquiryTracking } from "./pages/InquiryTracking";
import { AdminDashboard } from "./pages/AdminDashboard";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Home },
      { path: "catalog", Component: Catalog },
      { path: "coffee/:id", Component: CoffeeDetail },
      { path: "supplier-onboarding", Component: SupplierOnboarding },
      { path: "inquiries", Component: InquiryTracking },
      { path: "admin", Component: AdminDashboard },
    ],
  },
]);
