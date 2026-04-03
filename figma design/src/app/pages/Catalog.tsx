import { useState } from "react";
import { Link } from "react-router";
import { Search } from "lucide-react";

const mockLots = [
  {
    id: 1,
    name: "Monsooned Malabar AA",
    supplier: "Kerala Estate Co.",
    region: "Malabar",
    process: "Monsooned",
    cupScore: 87,
    tastingNotes: "Earthy, Low Acid, Chocolate",
    exportReady: true,
    sampleReady: true,
    verified: true,
    certifications: ["Organic"],
  },
  {
    id: 2,
    name: "Arabica Shade Grown",
    supplier: "Coorg Valley Farms",
    region: "Coorg",
    process: "Washed",
    cupScore: 89,
    tastingNotes: "Citrus, Floral, Honey",
    exportReady: true,
    sampleReady: true,
    verified: true,
    certifications: ["Fair Trade", "Organic"],
  },
  {
    id: 3,
    name: "Robusta Cherry AB",
    supplier: "Wayanad Collective",
    region: "Wayanad",
    process: "Natural",
    cupScore: 85,
    tastingNotes: "Bold, Nutty, Caramel",
    exportReady: true,
    sampleReady: false,
    verified: true,
    certifications: [],
  },
  {
    id: 4,
    name: "Estate Reserve Arabica",
    supplier: "Chikmagalur Estates",
    region: "Chikmagalur",
    process: "Washed",
    cupScore: 91,
    tastingNotes: "Jasmine, Bergamot, Dark Chocolate",
    exportReady: true,
    sampleReady: true,
    verified: true,
    certifications: ["Rainforest Alliance"],
  },
  {
    id: 5,
    name: "High Altitude Arabica",
    supplier: "Nilgiris Coffee Co.",
    region: "Nilgiris",
    process: "Honey",
    cupScore: 88,
    tastingNotes: "Apple, Caramel, Milk Chocolate",
    exportReady: false,
    sampleReady: true,
    verified: false,
    certifications: [],
  },
  {
    id: 6,
    name: "Heritage Blend",
    supplier: "Coorg Valley Farms",
    region: "Coorg",
    process: "Semi-Washed",
    cupScore: 86,
    tastingNotes: "Spice, Tobacco, Dried Fruit",
    exportReady: true,
    sampleReady: true,
    verified: true,
    certifications: ["Organic"],
  },
];

export function Catalog() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({
    region: "",
    varietal: "",
    certification: "",
    exportReady: false,
    sampleReady: false,
    verified: false,
  });

  const filteredLots = mockLots.filter((lot) => {
    if (searchQuery && !lot.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !lot.supplier.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (filters.region && lot.region !== filters.region) return false;
    if (filters.exportReady && !lot.exportReady) return false;
    if (filters.sampleReady && !lot.sampleReady) return false;
    if (filters.verified && !lot.verified) return false;
    if (filters.certification && !lot.certifications.includes(filters.certification)) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold mb-4">Coffee Catalog</h1>
          <p className="text-gray-600">Discover verified Indian coffee suppliers</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          <aside className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg border p-6 sticky top-24">
              <h2 className="font-semibold mb-4">Filters</h2>

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search lots or suppliers"
                    className="w-full pl-9 pr-3 py-2 border rounded-md text-sm"
                  />
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Region</label>
                <select
                  value={filters.region}
                  onChange={(e) => setFilters({ ...filters, region: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                >
                  <option value="">All regions</option>
                  <option value="Coorg">Coorg</option>
                  <option value="Wayanad">Wayanad</option>
                  <option value="Malabar">Malabar</option>
                  <option value="Nilgiris">Nilgiris</option>
                  <option value="Chikmagalur">Chikmagalur</option>
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Certification</label>
                <select
                  value={filters.certification}
                  onChange={(e) => setFilters({ ...filters, certification: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                >
                  <option value="">All certifications</option>
                  <option value="Organic">Organic</option>
                  <option value="Fair Trade">Fair Trade</option>
                  <option value="Rainforest Alliance">Rainforest Alliance</option>
                </select>
              </div>

              <div className="space-y-3">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={filters.exportReady}
                    onChange={(e) => setFilters({ ...filters, exportReady: e.target.checked })}
                    className="rounded"
                  />
                  Export Ready
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={filters.sampleReady}
                    onChange={(e) => setFilters({ ...filters, sampleReady: e.target.checked })}
                    className="rounded"
                  />
                  Ships Samples
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={filters.verified}
                    onChange={(e) => setFilters({ ...filters, verified: e.target.checked })}
                    className="rounded"
                  />
                  Verified Supplier
                </label>
              </div>

              <button
                onClick={() =>
                  setFilters({
                    region: "",
                    varietal: "",
                    certification: "",
                    exportReady: false,
                    sampleReady: false,
                    verified: false,
                  })
                }
                className="w-full mt-6 px-4 py-2 text-sm border rounded-md hover:bg-gray-50"
              >
                Clear Filters
              </button>
            </div>
          </aside>

          <div className="flex-1">
            <div className="mb-6 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                {filteredLots.length} {filteredLots.length === 1 ? "lot" : "lots"} found
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredLots.map((lot) => (
                <div
                  key={lot.id}
                  className="bg-white rounded-lg border hover:shadow-lg transition-shadow flex flex-col"
                >
                  <div className="p-6 flex flex-col flex-1">
                    <h3 className="font-semibold text-lg mb-2">{lot.name}</h3>
                    <p className="text-sm text-gray-600 mb-4">{lot.supplier}</p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {lot.exportReady && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          Export Ready
                        </span>
                      )}
                      {lot.sampleReady && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          Sample Ready
                        </span>
                      )}
                      {lot.verified && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                          Verified
                        </span>
                      )}
                    </div>

                    <dl className="space-y-2 text-sm mb-4">
                      <div className="flex justify-between">
                        <dt className="text-gray-600">Region</dt>
                        <dd className="font-medium">{lot.region}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-600">Process</dt>
                        <dd className="font-medium">{lot.process}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-600">Cup Score</dt>
                        <dd className="font-medium">{lot.cupScore}</dd>
                      </div>
                    </dl>

                    <p className="text-sm text-gray-600 mb-4">
                      <span className="font-medium">Notes:</span> {lot.tastingNotes}
                    </p>

                    <Link
                      to={`/coffee/${lot.id}`}
                      className="block w-full text-center px-4 py-2 bg-amber-700 text-white rounded hover:bg-amber-800 transition-colors mt-auto"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>

            {filteredLots.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600">No coffee lots match your filters</p>
                <button
                  onClick={() =>
                    setFilters({
                      region: "",
                      varietal: "",
                      certification: "",
                      exportReady: false,
                      sampleReady: false,
                      verified: false,
                    })
                  }
                  className="mt-4 px-6 py-2 bg-amber-700 text-white rounded hover:bg-amber-800"
                >
                  Clear All Filters
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
