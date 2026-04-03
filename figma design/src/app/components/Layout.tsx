import { Outlet, Link, useLocation } from "react-router";
import { Coffee } from "lucide-react";

export function Layout() {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="border-b bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              <Link to="/" className="flex items-center gap-2">
                <Coffee className="w-8 h-8 text-amber-700" />
                <span className="font-semibold text-lg">BeanAI</span>
              </Link>
              <div className="hidden md:flex gap-6">
                <Link
                  to="/catalog"
                  className={`px-3 py-2 rounded-md transition-colors ${
                    isActive("/catalog")
                      ? "bg-amber-50 text-amber-900"
                      : "text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  Catalog
                </Link>
                <Link
                  to="/supplier-onboarding"
                  className={`px-3 py-2 rounded-md transition-colors ${
                    isActive("/supplier-onboarding")
                      ? "bg-amber-50 text-amber-900"
                      : "text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  Suppliers
                </Link>
                <Link
                  to="/inquiries"
                  className={`px-3 py-2 rounded-md transition-colors ${
                    isActive("/inquiries")
                      ? "bg-amber-50 text-amber-900"
                      : "text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  Inquiries
                </Link>
                <Link
                  to="/admin"
                  className={`px-3 py-2 rounded-md transition-colors ${
                    isActive("/admin")
                      ? "bg-amber-50 text-amber-900"
                      : "text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  Admin
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <button className="px-4 py-2 text-sm bg-amber-700 text-white rounded-md hover:bg-amber-800 transition-colors">
                Sign In
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="bg-gray-50 border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-semibold mb-3">About</h3>
              <p className="text-sm text-gray-600">
                Source Indian specialty coffee with export and sample visibility
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-3">For Buyers</h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>Browse Coffee</li>
                <li>Request Samples</li>
                <li>Track Shipments</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-3">For Suppliers</h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>Join Platform</li>
                <li>List Coffee</li>
                <li>Manage Orders</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Support</h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>Help Center</li>
                <li>Compliance</li>
                <li>Contact</li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-600">
            © 2026 BeanAI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
