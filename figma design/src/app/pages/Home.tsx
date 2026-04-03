import { Link } from "react-router";
import { Search, Package, ShieldCheck, Truck, FileCheck, Globe } from "lucide-react";

export function Home() {
  return (
    <div>
      <section className="bg-gradient-to-b from-amber-50 to-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Source Indian Specialty Coffee with Export and Sample Visibility
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Discover verified suppliers, request samples, and track logistics and compliance for US imports
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                to="/catalog"
                className="px-6 py-3 bg-amber-700 text-white rounded-lg hover:bg-amber-800 transition-colors"
              >
                Browse Coffee
              </Link>
              <Link
                to="/supplier-onboarding"
                className="px-6 py-3 border-2 border-amber-700 text-amber-700 rounded-lg hover:bg-amber-50 transition-colors"
              >
                Join as Supplier
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Discover Suppliers</h3>
              <p className="text-gray-600">
                Browse verified Indian coffee suppliers with complete export readiness profiles
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Package className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Request Samples</h3>
              <p className="text-gray-600">
                Request coffee samples with transparent shipping and logistics visibility
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Truck className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Track Shipment and Compliance</h3>
              <p className="text-gray-600">
                Monitor shipment status and FDA Prior Notice compliance throughout delivery
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Built for Trust and Compliance</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg border">
              <ShieldCheck className="w-12 h-12 text-green-600 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Export-Ready Suppliers</h3>
              <p className="text-gray-600">
                All suppliers verified for international export capability with proper documentation
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg border">
              <Globe className="w-12 h-12 text-blue-600 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Sample Shipping Visibility</h3>
              <p className="text-gray-600">
                Track sample preparation, courier selection, and delivery timelines
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg border">
              <FileCheck className="w-12 h-12 text-purple-600 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Prior Notice Responsibility Tracking</h3>
              <p className="text-gray-600">
                Clear accountability for FDA Prior Notice filing on US-bound food shipments
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Featured Coffee Lots</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                name: "Monsooned Malabar AA",
                supplier: "Kerala Estate Co.",
                region: "Malabar",
                notes: "Earthy, Low Acid, Chocolate",
                score: 87,
              },
              {
                name: "Arabica Shade Grown",
                supplier: "Coorg Valley Farms",
                region: "Coorg",
                notes: "Citrus, Floral, Honey",
                score: 89,
              },
              {
                name: "Robusta Cherry AB",
                supplier: "Wayanad Collective",
                region: "Wayanad",
                notes: "Bold, Nutty, Caramel",
                score: 85,
              },
            ].map((lot, idx) => (
              <div key={idx} className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
                <h3 className="font-semibold text-lg mb-2">{lot.name}</h3>
                <p className="text-sm text-gray-600 mb-3">{lot.supplier}</p>
                <div className="flex gap-2 mb-3">
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    Export Ready
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    Sample Ready
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  <span className="font-medium">Region:</span> {lot.region}
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  <span className="font-medium">Cup Score:</span> {lot.score}
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  <span className="font-medium">Notes:</span> {lot.notes}
                </p>
                <Link
                  to={`/coffee/${idx + 1}`}
                  className="block text-center px-4 py-2 bg-amber-700 text-white rounded hover:bg-amber-800 transition-colors"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
