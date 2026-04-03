import { useState } from "react";
import { useParams, Link } from "react-router";
import { CheckCircle, X, AlertCircle } from "lucide-react";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";

const mockCoffeeData: Record<string, any> = {
  "1": {
    name: "Monsooned Malabar AA",
    supplier: "Kerala Estate Co.",
    region: "Malabar",
    process: "Monsooned",
    harvestYear: "2025",
    quantityAvailable: "5000 kg",
    priceIndication: "$8.50/kg FOB",
    altitude: "1100-1300m",
    varietals: "Arabica - Kent, S795",
    cupScore: 87,
    tastingNotes: "Earthy, Low Acid, Chocolate, Dried Fruit",
    estateStory:
      "Our estate has been producing the unique Monsooned Malabar coffee for over 100 years. The monsoon winds and moisture create a distinctive low-acid profile cherished by roasters worldwide.",
    certifications: ["Organic"],
    exportReady: true,
    sampleReady: true,
    sampleSize: "200g",
    couriers: ["DHL", "FedEx"],
    samplePrepTime: "2 days",
    sampleShippingTime: "5-7 days",
    complianceHandler: "Supplier",
    samplePrice: "$15",
    estateImage: "https://images.unsplash.com/photo-1652868965788-8c87bbba771b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBwbGFudGF0aW9uJTIwZmFybSUyMG1vdW50YWluc3xlbnwxfHx8fDE3NzM3MTAxNDd8MA&ixlib=rb-4.1.0&q=80&w=1080",
    coffeeImage: "https://images.unsplash.com/photo-1666873903780-396269c73a54?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwyfHxjb2ZmZWUlMjBiZWFucyUyMHJvYXN0ZWQlMjBzcGVjaWFsdHl8ZW58MXx8fHwxNzczNzEwMTQyfDA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  "2": {
    name: "Arabica Shade Grown",
    supplier: "Coorg Valley Farms",
    region: "Coorg",
    process: "Washed",
    harvestYear: "2025",
    quantityAvailable: "3000 kg",
    priceIndication: "$10.20/kg FOB",
    altitude: "1200-1500m",
    varietals: "Arabica - SL9, Chandragiri",
    cupScore: 89,
    tastingNotes: "Citrus, Floral, Honey, Bright Acidity",
    estateStory:
      "Nestled in the Western Ghats, our shade-grown coffee is cultivated under a canopy of native trees. This traditional method enhances flavor complexity while preserving biodiversity.",
    certifications: ["Fair Trade", "Organic"],
    exportReady: true,
    sampleReady: true,
    sampleSize: "250g",
    couriers: ["DHL", "FedEx", "UPS"],
    samplePrepTime: "1 day",
    sampleShippingTime: "4-6 days",
    complianceHandler: "Freight Forwarder",
    samplePrice: "$18",
    estateImage: "https://images.unsplash.com/photo-1684200379091-311db3682d7c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwyfHxjb2ZmZWUlMjBwbGFudGF0aW9uJTIwZmFybSUyMG1vdW50YWluc3xlbnwxfHx8fDE3NzM3MTAxNDd8MA&ixlib=rb-4.1.0&q=80&w=1080",
    coffeeImage: "https://images.unsplash.com/photo-1770081485131-d978211245aa?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHw0fHxjb2ZmZWUlMjBiZWFucyUyMHJvYXN0ZWQlMjBzcGVjaWFsdHl8ZW58MXx8fHwxNzczNzEwMTQyfDA&ixlib=rb-4.1.0&q=80&w=1080",
  },
};

export function CoffeeDetail() {
  const { id } = useParams();
  const coffee = mockCoffeeData[id || "1"] || mockCoffeeData["1"];
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestForm, setRequestForm] = useState({
    buyerName: "",
    company: "",
    email: "",
    country: "",
    sampleSize: coffee.sampleSize,
    message: "",
  });

  const handleSubmitRequest = (e: React.FormEvent) => {
    e.preventDefault();
    alert("Sample request submitted successfully!");
    setShowRequestModal(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link to="/catalog" className="text-sm text-amber-700 hover:underline mb-2 block">
            ← Back to Catalog
          </Link>
          <h1 className="text-3xl font-bold mb-2">{coffee.name}</h1>
          <p className="text-gray-600">{coffee.supplier}</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="rounded-lg overflow-hidden border">
                <ImageWithFallback
                  src={coffee.estateImage}
                  alt={`${coffee.supplier} estate`}
                  className="w-full h-64 object-cover"
                />
                <div className="p-2 bg-white text-xs text-gray-600 text-center">Estate View</div>
              </div>
              <div className="rounded-lg overflow-hidden border">
                <ImageWithFallback
                  src={coffee.coffeeImage}
                  alt={`${coffee.name} beans`}
                  className="w-full h-64 object-cover"
                />
                <div className="p-2 bg-white text-xs text-gray-600 text-center">Coffee Beans</div>
              </div>
            </div>

            <div className="bg-white rounded-lg border p-6">
              <h2 className="font-semibold text-lg mb-4">Overview</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm text-gray-600">Region</dt>
                  <dd className="font-medium">{coffee.region}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Process</dt>
                  <dd className="font-medium">{coffee.process}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Harvest Year</dt>
                  <dd className="font-medium">{coffee.harvestYear}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Quantity Available</dt>
                  <dd className="font-medium">{coffee.quantityAvailable}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Price Indication</dt>
                  <dd className="font-medium">{coffee.priceIndication}</dd>
                </div>
              </dl>
            </div>

            <div className="bg-white rounded-lg border p-6">
              <h2 className="font-semibold text-lg mb-4">Estate Story</h2>
              <p className="text-gray-700 leading-relaxed">{coffee.estateStory}</p>
            </div>

            <div className="bg-white rounded-lg border p-6">
              <h2 className="font-semibold text-lg mb-4">Coffee Specs</h2>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm text-gray-600">Altitude</dt>
                  <dd className="font-medium">{coffee.altitude}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Varietals</dt>
                  <dd className="font-medium">{coffee.varietals}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Cup Score</dt>
                  <dd className="font-medium">{coffee.cupScore}/100</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Tasting Notes</dt>
                  <dd className="font-medium">{coffee.tastingNotes}</dd>
                </div>
              </dl>
            </div>

            {coffee.certifications.length > 0 && (
              <div className="bg-white rounded-lg border p-6">
                <h2 className="font-semibold text-lg mb-4">Certifications</h2>
                <div className="flex flex-wrap gap-2">
                  {coffee.certifications.map((cert: string) => (
                    <span
                      key={cert}
                      className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                    >
                      {cert}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg border p-6">
              <h2 className="font-semibold text-lg mb-4">Logistics & Compliance</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <dt className="text-sm text-gray-600">Export Ready</dt>
                  <dd>
                    {coffee.exportReady ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <X className="w-5 h-5 text-red-600" />
                    )}
                  </dd>
                </div>
                <div className="flex items-center gap-2">
                  <dt className="text-sm text-gray-600">Ships Samples</dt>
                  <dd>
                    {coffee.sampleReady ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <X className="w-5 h-5 text-red-600" />
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Sample Size</dt>
                  <dd className="font-medium">{coffee.sampleSize}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Couriers</dt>
                  <dd className="font-medium">{coffee.couriers.join(", ")}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Sample Prep Time</dt>
                  <dd className="font-medium">{coffee.samplePrepTime}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600">Sample Shipping Time</dt>
                  <dd className="font-medium">{coffee.sampleShippingTime}</dd>
                </div>
                <div className="col-span-2">
                  <dt className="text-sm text-gray-600 mb-1">FDA Prior Notice</dt>
                  <dd className="font-medium">
                    Handled by {coffee.complianceHandler} for US shipments
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          <div>
            <div className="bg-white rounded-lg border p-6 sticky top-24">
              <h2 className="font-semibold text-lg mb-4">Request Sample</h2>

              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex gap-2">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-blue-800">
                    Prior Notice required for US-bound food shipments
                  </p>
                </div>
              </div>

              <dl className="space-y-3 mb-6 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-600">Sample Size</dt>
                  <dd className="font-medium">{coffee.sampleSize}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Sample Price</dt>
                  <dd className="font-medium">{coffee.samplePrice}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Prep + Shipping</dt>
                  <dd className="font-medium">
                    {parseInt(coffee.samplePrepTime) +
                      parseInt(coffee.sampleShippingTime.split("-")[0])}{" "}
                    days
                  </dd>
                </div>
              </dl>

              <button
                onClick={() => setShowRequestModal(true)}
                className="w-full px-6 py-3 bg-amber-700 text-white rounded-lg hover:bg-amber-800 transition-colors"
              >
                Request Sample
              </button>

              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600">
                  Questions about this coffee?
                  <br />
                  <a href="#" className="text-amber-700 hover:underline">
                    Contact {coffee.supplier}
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showRequestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <h2 className="text-xl font-bold">Request Sample</h2>
              <button
                onClick={() => setShowRequestModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmitRequest} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Your Name *</label>
                <input
                  type="text"
                  value={requestForm.buyerName}
                  onChange={(e) =>
                    setRequestForm({ ...requestForm, buyerName: e.target.value })
                  }
                  required
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Company *</label>
                <input
                  type="text"
                  value={requestForm.company}
                  onChange={(e) => setRequestForm({ ...requestForm, company: e.target.value })}
                  required
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Email *</label>
                <input
                  type="email"
                  value={requestForm.email}
                  onChange={(e) => setRequestForm({ ...requestForm, email: e.target.value })}
                  required
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Destination Country *</label>
                <select
                  value={requestForm.country}
                  onChange={(e) => setRequestForm({ ...requestForm, country: e.target.value })}
                  required
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="">Select country</option>
                  <option value="US">United States</option>
                  <option value="UK">United Kingdom</option>
                  <option value="AU">Australia</option>
                  <option value="CA">Canada</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {requestForm.country === "US" && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex gap-2">
                    <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-800">
                      <p className="font-medium mb-1">FDA Prior Notice Required</p>
                      <p>
                        For this shipment, {coffee.complianceHandler.toLowerCase()} will handle
                        Prior Notice filing.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-1">Requested Sample Size</label>
                <input
                  type="text"
                  value={requestForm.sampleSize}
                  onChange={(e) => setRequestForm({ ...requestForm, sampleSize: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Message to Supplier</label>
                <textarea
                  value={requestForm.message}
                  onChange={(e) => setRequestForm({ ...requestForm, message: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md h-24"
                  placeholder="Any specific requests or questions..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowRequestModal(false)}
                  className="flex-1 px-6 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-6 py-2 bg-amber-700 text-white rounded-lg hover:bg-amber-800"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
